"""
We are trying to create a bot that can communicate through the LLM model.
The ability to give commands through `/` in Telegram and chat with bots in general conversations.
"""
import logging
from telegram import BotCommand
from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler

# Load bot commands
from Commands import *

# Load the Telegram bot API key
from dotenv import load_dotenv
import os


class Agent(object):

    def __init__(self):
        """
        Initializes the Agent object by loading the Telegram bot token
        from the environment and setting up the application, logging,
        and bot commands.
        """
        load_dotenv()
        TOKEN = os.getenv("BOT_TOKEN")
        self.application = ApplicationBuilder().token(TOKEN).build()

        self._setup_logging()
        self._command_preview()

    def update_handler(self):
        """
        Configures the handlers for various commands and text-based inputs.
        It adds handlers for commands such as 'start', 'help', 'weather', and general text messages.
        Additionally, an unknown command handler is added for unrecognized inputs.

        Handlers added:
        - 'start': Initializes the bot interaction.
        - 'help': Provides help information.
        - 'weather': Returns weather information.
        - Text messages (non-command): Responds with a GPT response.
        - Unknown commands: Responds to unrecognized commands.

        Runs the polling process to listen for incoming messages.
        """
        start_handler = CommandHandler('start', Start)
        self.application.add_handler(start_handler)

        help_handler = CommandHandler('help', Help)
        self.application.add_handler(help_handler)

        weather_handler = CommandHandler('weather', Weather)
        self.application.add_handler(weather_handler)

        self.application.add_handler(CommandHandler('gpt', GPT_response))
        self.application.add_handler(CallbackQueryHandler(Handle_callback_query))

        unknown_handler = MessageHandler(filters.COMMAND, Unknown)
        self.application.add_handler(unknown_handler)

        self.application.run_polling()

    def _setup_logging(self):
        """
        Sets up logging for the application with a specific log format
        and log level set to INFO.
        """
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    def _command_preview(self):
        """
        Registers the bot commands that users can call, such as 'help' and 'weather'.
        These commands provide descriptions for use in the bot interface.
        """
        commands_list = [
            BotCommand(command="help", description="도움말 보기"),
            BotCommand(command="weather", description="날씨 정보 확인"),
            BotCommand(command="gpt", description="GPT 질문")
        ]
        self.application.bot.set_my_commands(commands_list)


if __name__ == '__main__':
    agent = Agent()
    agent.update_handler()