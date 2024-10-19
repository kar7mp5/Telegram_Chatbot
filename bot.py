#! ./venv/bin/python3

"""
bot.py

We are trying to create a bot that can communicate through the LLM model.
The ability to give commands through `/` in Telegram and chat with bots in general conversations.
"""

import logging
from telegram import BotCommand
from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler

# Load bot commands
import commands


# Load the Telegram bot API key
from dotenv import load_dotenv
import os




class Agent(object):
    
    def __init__(self):
        # Load telegram token
        load_dotenv()
        TOKEN = os.getenv("BOT_TOKEN")

        self.application = ApplicationBuilder().token(TOKEN).build()
        self.setup_logging()
        self.command_preview()


    def setup_logging(self):
        # Set up the log style
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )


    def command_preview(self):
        # Register bot commands for preview
        commands_list = [
            BotCommand(command="help", description="도움말 보기"),
            BotCommand(command="weather", description="날씨 정보 확인")
        ]
        self.application.bot.set_my_commands(commands_list)


    def update_handler(self):
        # Handlers
        start_handler = CommandHandler('start', commands.start)
        self.application.add_handler(start_handler)

        help_handler = CommandHandler('help', commands.help)
        self.application.add_handler(help_handler)

        weather_handler = CommandHandler('weather', commands.weather)
        self.application.add_handler(weather_handler)

        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, commands.gpt_response))

        # Other handlers
        unknown_handler = MessageHandler(filters.COMMAND, commands.unknown)
        self.application.add_handler(unknown_handler)

        self.application.run_polling()




if __name__ == '__main__':
    agent = Agent()
    agent.update_handler()
