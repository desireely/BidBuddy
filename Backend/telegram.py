import telebot 
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import requests
import random

from dotenv.main import load_dotenv

listing_URL = "http://listing:5007/listing"
bid_URL = "http://bid:5020/bid"
user_URL = "http://user:5005/user"
showdetailsofbids_URL = "http://showdetailsofbids:5002/showdetailsofbids"
bidforlisting_URL = "http://bidforlisting:5015/bidforlisting"

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.environ['TELEBOT_API_KEY']

bot = telebot.TeleBot(API_KEY)


print("------------------TELEGRAM BOT RUNNING--------------------")
@bot.message_handler(commands=['start'])
def start(message):
    # get the user's handle
    handle = message.chat.username
    start_message = f"Hello @{handle}! Welcome to BidBuddy Telebot! How can we help you?"
    bot.send_message(message.chat.id, start_message)

greetings = ['Hello! How can we help you?', 'Yo, bidding legend! BidBuddy is at your service!', 'Greetings, bidder extraordinaire! How can BidBuddy help you?', 'Hey there, bidding superstar!']

@bot.message_handler(func=lambda message: message.text.lower() == 'hello')
def send_greeting(message):
    greeting = random.choice(greetings)
    bot.send_message(message.chat.id, greeting)



#help to list out command functions
@bot.message_handler(commands=['help'])

def help(message):
    help_message = """Here is the list of commands you can use:
/mylistings = Get all the listings that you posted up for auction
/mybids = Get all the listings that you are currently bidding for
/placebids = Submit a new bid on a particular listing
"""
    bot.send_message(message.chat.id, help_message)
    

#notification 

# @bot.message_handler(commands=['notify'])

# def send_notification(message):
#     data = rabbitconsume.data
#     print(data)
#     receiver = message.chat.username
#     if receiver in data["user_teles"]:
#         bot.send_message(message.chat.id, data["subject"])
#         # rabbitconsume.clear_data()



# GET MY BIDS
@bot.message_handler(commands=['mylistings'])

def mybids(message):
    tele_id = message.chat.username
    message_id = message.chat.id
    print(tele_id)

    user_details = requests.get(f'{user_URL}/tele/{tele_id}').json()
    print(user_details)
    userid = user_details["data"]["userid"]
    # {'teleuser': 'clovis_c', 'userid': 'ovY4jIpP4TZFjrz7pTEf9PknRlM2', 'email': 'clovischowjh@gmail.com', 'username': 'clovis'}

    response = requests.get(f'{listing_URL}/user/{userid}')

    if response.status_code == 200 and response.json()['code'] != 404:
        # Retrieve user data from API response
        print("---------------------------------------------")
        print(response)
        user_data = response.json()
        print(user_data)
        print(response.json()['code'])
        listings = user_data['data']['listings']
        number = 1
        # Send user data as a message to the user in Telegram
        listingmsg = "List of listings:\n"
        for listing in listings:
            listingmsg += f"""{number}. {listing['listing_name']} (Listing ID: {listing['listingid']}) \n    Current Bid: {listing['highest_current_bid']} \n"""
            number += 1
        bot.send_message(chat_id=message_id, text=listingmsg)
    else:
        # Send error message if request failed
        bot.send_message(chat_id=message_id, text='Sorry, you do not have any ongoing bids')


# GET MY BIDS
@bot.message_handler(commands=['mybids'])

def mybids(message):
    tele_id = message.chat.username
    message_id = message.chat.id
    print(tele_id)

    user_details = requests.get(f'{user_URL}/tele/{tele_id}').json()
    print(user_details)
    userid = user_details["data"]["userid"]
    # {'teleuser': 'clovis_c', 'userid': 'ovY4jIpP4TZFjrz7pTEf9PknRlM2', 'email': 'clovischowjh@gmail.com', 'username': 'clovis'}

    response = requests.get(f'{showdetailsofbids_URL}/{userid}')

    if response.status_code == 200 and response.json()['code'] != 404:
        # Retrieve user data from API response
        print("---------------------------------------------")
        print(response)
        user_data = response.json()
        print(user_data)
        print(response.json()['code'])
        listings = user_data['data']
        number = 1
        # Send user data as a message to the user in Telegram
        listingmsg = "List of bids:\n"
        for listing in listings:
            listingmsg += f"""{number}. {listing['listing_name']} (Listing ID: {listing['listingid']}) \n    Current Bid: {listing['highest_current_bid']} \n"""
            number += 1
        bot.send_message(chat_id=message_id, text=listingmsg)
    else:
        # Send error message if request failed
        bot.send_message(chat_id=message_id, text='Sorry, you do not have any ongoing bids')



#GET 1 SPECIFIC LISTING, THEN DISPLAY INFO, THEN ASK FOR NEW BID AMOUNT
@bot.message_handler(commands=['placebids'])

def getlistingid(message):

    bot.send_message(chat_id=message.chat.id, text="What's the listing ID?")
    bot.register_next_step_handler(message, showlisting)

def showlisting(message):
    tele_id = message.chat.username
    user_details = requests.get(f'{user_URL}/tele/{tele_id}').json()
    user_id = user_details["data"]["userid"]
    message_id = message.chat.id
    listingid = message.text
    response = requests.get(f'{listing_URL}/{listingid}')

    if response.status_code == 200:
        # Retrieve user data from API response
        listing_json = response.json()
        listing = listing_json['data']
        # Send user data as a message to the user in Telegram
        listingmsg = f"""{listing['listing_name']} (Listing ID: {listing['listingid']}) \nCurrent Bid: {listing['highest_current_bid']} \n"""
        bot.send_message(chat_id=message_id, text=listingmsg)

        bot.send_message(chat_id=message_id, text="What is the amount you want to bid?")
        bot.register_next_step_handler(message, updatebids, listingid, user_id)
    else:
        # Send error message if request failed
        bot.send_message(chat_id=message_id, text='Sorry, the listing ID you entered is invalid.')


def updatebids(message, listingid, user_id):
    message_id = message.chat.id
    bid_price = float(message.text)
    bid_details = {'listing_id': listingid, 'user_id': user_id, 'bid_price': bid_price,}

    response = requests.post(f'{bidforlisting_URL}', json=bid_details) 

    if response.status_code == 201:
        # Retrieve user data from API response
        bid_summary = response.json()

        # Send user data as a message to the user in Telegram
        message = f"Success! You bidded ${bid_price} for listingid:{listingid}"
        bot.send_message(chat_id=message_id, text=message)
    else:
        # Send error message if request failed
        print(response.json())
        bot.send_message(chat_id=message_id, text='Bid Failed. Please check if you placed a bid higher than the current bid')



@bot.message_handler(func=lambda message: True)
def send_instructions(message):
    messages = ["Sorry, I didn't understand that. Please use the /help command for assistance.",
                "I'm not sure what you mean. You can try using the /help command for more information.",
                "Hmm, that's not a command I recognize. Try using the /help command for assistance."]
    response = random.choice(messages)
    bot.reply_to(message, response)
























#test
# @bot.message_handler(commands=['book'])

# def start(message):
#     bot.send_message(chat_id=message.chat.id, text="What's the ISBN?")

#     # Set the next expected message from the user as the 'name' command
#     bot.register_next_step_handler(message, user_info)


# def user_info(message):
#     user_id = message.chat.id

#     # Get the user ID of the person who sent the message
#     ISBN = message.text

#     # Call the user microservice API to get user data
#     response = requests.get(f'http://127.0.0.1:5000/book/{ISBN}')


#     if response.status_code == 200:
#         # Retrieve user data from API response
#         user_data = response.json()

#         # Send user data as a message to the user in Telegram
#         message = f"Availability: {user_data['data']['availability']}\nISBN13: {user_data['data']['isbn13']}\nPrice: {user_data['data']['price']}\nTitle: {user_data['data']['title']}"
#         bot.send_message(chat_id=user_id, text=message)
#     else:
#         # Send error message if request failed
#         bot.send_message(chat_id=user_id, text='Sorry, we cannot find your book')


bot.polling()

# Run script
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5019, debug=True)