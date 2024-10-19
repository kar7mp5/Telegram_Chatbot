#! ./venv/bin/python

"""
bot.py

We are trying to create a bot that can communicate through the LLM model.
The ability to give commands through `/` in Telegram and chat with bots in general conversations.
"""

import logging
from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler

# Load bot commands
import commands


# Load the Telegram bot API key
from dotenv import load_dotenv
import os




def main():
    # Set up the log style
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )


    # Load telegram token
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")

    application = ApplicationBuilder().token(TOKEN).build()


    # Handlers
    help_handler = CommandHandler('help', commands.help)
    application.add_handler(help_handler)

    weather_handler = CommandHandler('weather', commands.weather)
    application.add_handler(weather_handler)
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, commands.gpt_response))


    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, commands.unknown)
    application.add_handler(unknown_handler)

    application.run_polling()




if __name__ == '__main__':
    main()
