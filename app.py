#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import sys
import json
from flask_heroku import Heroku
from pymessenger.bot import Bot
import os 

import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)

today = datetime.date.today().strftime("%B %d, %Y")

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']

bot = Bot (ACCESS_TOKEN)

class Ulamentry(db.Model):
    __tablename__ = "ulam_sa_pantry"
    #id = db.Column(db.Integer, primary_key=True)
    floor = db.Column(db.Text(), primary_key=True)
    date = db.Column(db.Text())
    ulam = db.Column(db.Text())

    def __init__(self, floor, date, ulam):
        self.date = date
        self.floor = floor
        self.ulam = ulam

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        #return token_sent
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       print(output)
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            recipient_id = message['sender']['id']

            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                
                
                if message['message'].get('text'):
                    user_msg = message['message'].get('text')
                    
                    if 'iamearly' in user_msg:
                        if '9F' in user_msg:
                            #input_ulam = Ulamentry('9F', '20190516', user_msg.split('iamearly',1)[-1].strip())
                            response_sent_text = update_ulam('9F', today, user_msg.split('iamearly',1)[-1].strip())
                        elif '14F' in user_msg:
                            #input_ulam = Ulamentry('14F', '20190516', user_msg.split('iamearly',1)[-1].strip())
                            response_sent_text = update_ulam('14F', today, user_msg.split('iamearly',1)[-1].strip())
                            
                    elif '9F' in user_msg:
                        response_sent_text = get_ulam('9F')
                        
                    elif '14F' in user_msg:
                        response_sent_text = get_ulam('14F')
                    else:
                        response_sent_text = 'Gusto mo bang malaman ang ulam today?'
                        buttons = [{"type": "postback", "title":"Ano meron sa 9F?", "payload": "9F"}, {"type": "postback", "title":"Ano meron sa 14F?", "payload": "14F"}]
                        bot.send_button_message(recipient_id, response_sent_text, buttons)
                        
                    #response_sent_text = get_message()
                    send_message(recipient_id, response_sent_text)

                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
            elif message.get('postback'):
                user_msg = message['postback']['payload']
                print('this is postback')
                print(user_msg)
                    
                if '9F' == user_msg:
                    response_sent_text = get_ulam('9F')
                        
                elif '14F' == user_msg:
                    response_sent_text = get_ulam('14F')

                    send_message(recipient_id, response_sent_text)

    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'test'

def get_ulam(floor):
    pantry = Ulamentry.query.filter_by(floor=floor).first()
    ulam = pantry.ulam
    date = pantry.date

    reply = 'Ang ulam today(' + date + ') sa ' + floor + ' ay ' + ulam
    return reply

def update_ulam(floor, date, ulam):
    pantry = Ulamentry.query.filter_by(floor=floor).first()
    pantry.ulam = ulam
    pantry.date = date

    try:
        db.session.commit()
    except Exception as e:
        print('It failed :(')
        print(e)
        sys.stdout.flush()

    reply = 'Thank you for the info!!!'
    return reply

#chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    
    return "success"

if __name__ == "__main__":
    app.run()
