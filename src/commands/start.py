from telegram import Update
from telegram.ext import ContextTypes
from tools import send_message, setup_logger
import logging

# Initialize the logger configuration
setup_logger()
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the `/start` command.

    Sends a welcome message to the user and logs the interaction details,
    including user information and chat metadata.

    Args:
        update (Update): Incoming update containing the message from the user.
        context (ContextTypes.DEFAULT_TYPE): Provides context for the update, 
                                              including message metadata.

    Logging:
        - INFO: Logs when a user starts interacting with the bot.
    """
    user = update.effective_user  # Get user information
    chat_id = update.effective_chat.id

    # Log the user interaction
    logger.info(f"Bot started by user '{user.username}' (ID: {user.id}) in chat ID: {chat_id}")

    # Send a welcome message to the user
    await send_message(
        update=update,
        context=context,
        text="*I'm a bot, please talk to me!*"
    )