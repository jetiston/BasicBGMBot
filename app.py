#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import sys
import json
from flask_heroku import Heroku
from pymessenger.bot import Bot
import os 

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
ULAM_9F = os.environ['ULAM_9F']
ULAM_14F = os.environ['ULAM_14']
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
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                
                if message['message'].get('text'):
                    user_msg = message['message'].get('text')
                    
                    if 'iamearly' in user_msg:
                        if '9F' in user_msg:
                            input_ulam = Ulamentry('9F', '20190516', user_msg.split('iamearly',1)[-1].strip())
                        elif '14F' in user_msg:
                            input_ulam = Ulamentry('14F', '20190516', user_msg.split('iamearly',1)[-1].strip())

                        try:
                            db.session.add(input_ulam)
                            db.session.commit()
                        except Exception as e:
                            print('It failed :(')
                            print(e)
                            sys.stdout.flush()

                        response_sent_text = 'Thanks for the info!'
                            
                    elif '9F' in user_msg:
                        response_sent_text = ULAM_9F
                        
                    elif '14F' in user_msg:
                        response_sent_text = ULAM_14F
                    else:
                        response_sent_text = 'Aw, walang foods diyan'
                        
                    #response_sent_text = get_message()
                    send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
                    
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'test'


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
