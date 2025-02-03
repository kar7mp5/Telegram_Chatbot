from telegram import Update
from telegram.ext import ContextTypes
from tools import send_message, setup_logger
import logging

# Initialize the logger configuration
setup_logger()
logger = logging.getLogger(__name__)

async def Help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the `/help` command.

    Provides information about available bot commands and logs the interaction,
    including user and chat details.

    Args:
        update (Update): Incoming update containing the message from the user.
        context (ContextTypes.DEFAULT_TYPE): Provides context for the update,
                                              including message metadata.

    Logging:
        - INFO: Logs when a user requests help information.
    """
    user = update.effective_user  # Get user information
    chat_id = update.effective_chat.id

    # Log the help command request
    logger.info(f"Help command requested by user '{user.username}' (ID: {user.id}) in chat ID: {chat_id}")

    # Send help message with available commands
    await send_message(
        update=update,
        context=context,
        text="""\
`/help` - Show all commands
`/weather <city>` - Show weather forecast for the specified city
`/gpt <prompt>` - Ask GPT a question
"""
    )