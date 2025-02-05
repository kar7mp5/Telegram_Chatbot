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
        handlers = [
            (CommandHandler("start", start), "/start"),
            (CommandHandler("help", help), "/help"),
            (CommandHandler("weather", weather), "/weather"),
            (CommandHandler("gpt", gpt_response), "/gpt"),
            (CallbackQueryHandler(handle_callback_query, pattern="^gpt_.*"), "gpt callback"),
            (CommandHandler("test", test_response), "/test"),
            (CommandHandler("empty", empty), "/empty"),
            (CallbackQueryHandler(button_handler, pattern="^test_.*"), "test callback")
        ]

        logger.info("Initializing command handlers...")
        for handler, description in handlers:
            self.application.add_handler(handler)
            logger.info(f"Handler added for '{description}' command.")
        
        # self.application.add_handler(CommandHandler('start', start))
        # logger.info("Handler added for '/start' command.")

        # self.application.add_handler(CommandHandler('help', help))
        # logger.info("Handler added for '/help' command.")

        # self.application.add_handler(CommandHandler('weather', weather))
        # logger.info("Handler added for '/weather' command.")

        # self.application.add_handler(CommandHandler('gpt', gpt_response))
        # self.application.add_handler(CallbackQueryHandler(handle_callback_query, pattern="^gpt_.*"))
        # logger.info("Handler added for '/gpt' command.")

        # self.application.add_handler(CommandHandler('test', test_response))
        # self.application.add_handler(CallbackQueryHandler(button_handler, pattern="^test_.*"))
        # logger.info("Handler added for '/test' command.")

        unknown_handler = MessageHandler(filters.COMMAND, unknown)
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
            BotCommand(command="gpt", description="Ask GPT a qestion!"),
            BotCommand(command="test", description="Test command"),
            BotCommand(command="empty", description="Empty chat history")
        ]
        await application.bot.set_my_commands(commands_list)


if __name__ == '__main__':
    agent = Agent()
    agent.update_handler()