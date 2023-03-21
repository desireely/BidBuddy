from telegram.ext import *
import Responses as R
import os
from dotenv.main import load_dotenv

load_dotenv()

print ("Bot started...")

def start_command(update, context):
    update.message.reply_text('Type something random to get started!')


def help_command(update, context):
    update.message.reply_text('If you need help, you should ask for it on Google!')

def handle_message(update, context):
    text= str(update.message.text).lower()
    response = R.sample_responses(text)

    update.message.reply_text(response)

def error(update,context):
    print(f"Update {update} caused error {context.error}")


def main():
    updater = Updater(os.environ['TELEBOT_API_KEY'])
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("start", help_command))
    
    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

main()