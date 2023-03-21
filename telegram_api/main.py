import telebot 
import Responses as R
import os
import requests
from dotenv.main import load_dotenv

load_dotenv()

API_KEY = os.environ['TELEBOT_API_KEY']

bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['Greet'])
def greet(message):
    bot.reply_to(message, "Hey! Hows it going")

@bot.message_handler(commands=['hello'])
def hello(message):
    bot.send_message(message.chat.id, "Hello!")


#retrieve items user is currently putting up for listing
@bot.message_handler(commands=['mylisting'])

def start(message):
    bot.send_message(chat_id=message.chat.id, text="What's your username?")

    # Set the next expected message from the user as the 'name' command
    bot.register_next_step_handler(message, user_info)


def user_info(message):
    # Get the user ID of the person who sent the message
    user_id = message.text

    # Call the user microservice API to get user data
    response = requests.get(f'http://user-microservice/api/v1/users/{user_id}')


    if response.status_code == 200:
        # Retrieve user data from API response
        user_data = response.json()

        # Send user data as a message to the user in Telegram
        message = f"Name: {user_data['name']}\nEmail: {user_data['email']}\nPhone: {user_data['phone']}"
        bot.send_message(chat_id=message.chat.id, text=message)
    else:
        # Send error message if request failed
        bot.send_message(chat_id=message.chat.id, text='Unable to retrieve user data')

bot.polling()