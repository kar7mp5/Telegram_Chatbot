#! ./venv/bin/python
# bot.py
import logging
from telegram.ext import filters, ApplicationBuilder, CommandHandler, InlineQueryHandler, MessageHandler, ContextTypes

# Load bot commands
import commands


# Load the Telegram bot API key
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


# Set up the log style
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)




if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    help_handler = CommandHandler('help', commands.help)
    application.add_handler(help_handler)

    weather_handler = CommandHandler('weather', commands.weather)
    application.add_handler(weather_handler)

    # inlinequery_handler = InlineQueryHandler(commands.inline_query)
    # application.add_handler(inlinequery_handler)
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, commands.gpt_response))

    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, commands.unknown)
    application.add_handler(unknown_handler)

    application.run_polling()
