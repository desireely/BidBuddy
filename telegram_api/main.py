import telebot 
import os
import requests
import pika
import amqp_setup
import json
from dotenv.main import load_dotenv

load_dotenv()

API_KEY = os.environ['TELEBOT_API_KEY']

bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    # get the user's handle
    handle = message.chat.username
    start_message = f"Hello @{handle}! Welcome to BidBuddy Telebot! How can we help you?"
    bot.send_message(message.chat.id, start_message)

@bot.message_handler(commands=['Greet'])
def greet(message):
    bot.reply_to(message, "Hey! Hows it going")

@bot.message_handler(commands=['hello'])
def hello(message):
    bot.send_message(message.chat.id, "Hello!")


#retrieve list of items user is currently bidding
@bot.message_handler(commands=['mybids'])

def start(message):
    bot.send_message(chat_id=message.chat.id, text="What's your username?")

    # Set the next expected message from the user as the 'name' command
    bot.register_next_step_handler(message, user_info)


def user_info(message):
    user_id = message.chat.id
    # Get the user ID of the person who sent the message
    user_id = message.text

    # Call the user microservice API to get user data
    response = requests.get(f'http://127.0.0.1:5000/listing/{user_id}')


    if response.status_code == 200:
        # Retrieve user data from API response
        user_data = response.json()

        # Send user data as a message to the user in Telegram
        message = f"Name: {user_data['name']}\nEmail: {user_data['email']}\nPhone: {user_data['phone']}"
        bot.send_message(chat_id=user_id, text=message)
    else:
        # Send error message if request failed
        bot.send_message(chat_id=message.chat.id, text='Unable to retrieve user data')

#help to list out command functions
@bot.message_handler(commands=['help'])

def help(message):
    help_message = """Here is the list of commands you can use:
/mybids = Get all the listings that you are currently bidding for
/placebids = Submit a new bid on a listing
"""
    bot.send_message(message.chat.id, help_message)
    

#notification 
amqp_setup.check_setup()
        
queue_name = 'send_tele'

def notification(body):
    # send the message as a notification to the Telegram bot
    # get the latest updates from Telegram
    updates = bot.get_updates()
    # get the first chat in the list of updates
    chat = updates[-1].message.chat
    handle = chat.username
    data = json.loads(body)
    if handle in data["user_teles"]:
        bot.send_message(chat.id, body.decode())
    
# set up a consumer and start to wait for coming messages
amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=notification, auto_ack=True)
amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
#it doesn't exit by default. Use Ctrl+C in the command window to terminate it.



#test
@bot.message_handler(commands=['book'])

def start(message):
    bot.send_message(chat_id=message.chat.id, text="What's the ISBN?")

    # Set the next expected message from the user as the 'name' command
    bot.register_next_step_handler(message, user_info)


def user_info(message):
    user_id = message.chat.id

    # Get the user ID of the person who sent the message
    ISBN = message.text

    # Call the user microservice API to get user data
    response = requests.get(f'http://127.0.0.1:5000/book/{ISBN}')


    if response.status_code == 200:
        # Retrieve user data from API response
        user_data = response.json()

        # Send user data as a message to the user in Telegram
        message = f"Availability: {user_data['data']['availability']}\nISBN13: {user_data['data']['isbn13']}\nPrice: {user_data['data']['price']}\nTitle: {user_data['data']['title']}"
        bot.send_message(chat_id=user_id, text=message)
    else:
        # Send error message if request failed
        bot.send_message(chat_id=user_id, text='Sorry, we cannot find your book')


bot.polling()