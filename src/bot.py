"""
We are trying to create a bot that can communicate through the LLM model.
The ability to give commands through `/` in Telegram and chat with bots in general conversations.
"""
from telegram import BotCommand
from telegram.ext import *

from tools import setup_logger
from dotenv import load_dotenv
import logging
import os

# Load bot commands
from commands import *

# Initialize the logger configuration
setup_logger()
logger = logging.getLogger(__name__)


class Agent:

    def __init__(self):
        """
        Initializes the Agent object by loading the Telegram bot token
        from the environment and setting up the application, logging,
        and bot commands.
        """
        load_dotenv()
        TOKEN = os.getenv("BOT_TOKEN")

        self.application = (
            ApplicationBuilder()
            .token(TOKEN)
            .post_init(self._post_init)
            .build()
        )

    def update_handler(self):
        """
        Configures the handlers for commands and starts polling for updates.
        """
        logger.info("Initializing command handlers...")

        start_handler = CommandHandler('start', Start)
        self.application.add_handler(start_handler)
        logger.info("Handler added for /start command.")

        help_handler = CommandHandler('help', Help)
        self.application.add_handler(help_handler)
        logger.info("Handler added for /help command.")

        weather_handler = CommandHandler('weather', Weather)
        self.application.add_handler(weather_handler)
        logger.info("Handler added for /weather command.")

        self.application.add_handler(CommandHandler('gpt', GPT_response))
        logger.info("Handler added for /gpt command.")

        self.application.add_handler(CallbackQueryHandler(Handle_callback_query))
        logger.info("Callback query handler added.")

        unknown_handler = MessageHandler(filters.COMMAND, Unknown)
        self.application.add_handler(unknown_handler)
        logger.info("Unknown command handler added.")

        try:
            logger.info("Bot is starting polling...")
            self.application.run_polling()
        except Exception as e:
            logger.error(f"An error occurred during polling: {e}")

    async def _post_init(self, application: Application):
        """
        Registers the bot commands that users can call.
        These commands provide descriptions for use in the bot interface.
        
        Args:
            application (telegram.ext.Application): This class dispatches all kinds of updates to its registered handlers, and is the entry point to a PTB application.
        """
        commands_list: list[BotCommand] = [
            BotCommand(command="help", description="Shows the help menu"),
            BotCommand(command="weather", description="Displays current weather info"),
            BotCommand(command="gpt", description="Ask GPT a qestion!")
        ]
        await application.bot.set_my_commands(commands_list)


if __name__ == '__main__':
    agent = Agent()
    agent.update_handler()