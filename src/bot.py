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

class Agent:
    # Initialize the logger configuration
    setup_logger()
    logger = logging.getLogger(__name__)

    # Load environment variables
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")

    def __init__(self):
        """
        Initializes the Agent object by loading the Telegram bot token
        from the environment and setting up the application, logging,
        and bot commands.
        """
        self.application = (
            ApplicationBuilder()
            .token(self.TOKEN)
            .post_init(self._post_init)
            .build()
        )

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
            BotCommand(command="search", description="Ask GPT a qestion with web search"),
            BotCommand(command="test", description="Test command"),
            BotCommand(command="empty", description="Empty chat history")
        ]
        await application.bot.set_my_commands(commands_list)

    def update_handler(self):
        """
        Configures the handlers for commands and starts polling for updates.
        """
        gpt_agent = GPT_Agent()
        handlers = [
            (CommandHandler("start", start), "/start"),
            (CommandHandler("help", help), "/help"),
            (CommandHandler("weather", weather), "/weather"),
            (CommandHandler("gpt", gpt_agent.gpt_response), "/gpt"),
            (CommandHandler("search", gpt_agent.search_response), "/search"),
            (CallbackQueryHandler(gpt_agent.handle_callback_query, pattern="^gpt_.*"), "gpt callback"),
            (CommandHandler("test", test_response), "/test"),
            (CommandHandler("empty", empty), "/empty"),
            (CallbackQueryHandler(button_handler, pattern="^test_.*"), "test callback")
        ]

        self.logger.info("Initializing command handlers...")
        for handler, description in handlers:
            self.application.add_handler(handler)
            self.logger.info(f"Handler added for '{description}' command.")
        
        unknown_handler = MessageHandler(filters.COMMAND, unknown)
        self.application.add_handler(unknown_handler)
        self.logger.info("Unknown command handler added.")

        try:
            self.logger.info("Bot is starting polling...")
            self.application.run_polling()
        except Exception as e:
            self.logger.error(f"An error occurred during polling: {e}")


if __name__ == '__main__':
    agent = Agent()
    agent.update_handler()