from telegram import Update
from telegram.ext import ContextTypes
from tools import send_message, setup_logger
import logging

# Initialize the logger configuration
setup_logger()
logger = logging.getLogger(__name__)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles unknown or unrecognized commands.

    Sends a message to the user indicating that the command was not understood
    and logs the unrecognized command for debugging purposes.

    Args:
        update (Update): Incoming update containing the message from the user.
        context (ContextTypes.DEFAULT_TYPE): Provides context for the update, 
                                              including message metadata.

    Logging:
        - INFO: Logs the unknown command with user information.
    """
    user = update.effective_user  # Get user info (username, ID)
    command = update.message.text if update.message else "Unknown command"

    # Log the unrecognized command along with user details
    logger.info(f"Unknown command received from user '{user.username}' (ID: {user.id}): {command}")

    # Send a reply to the user
    await send_message(
        update=update,
        context=context,
        text="*Sorry, I didn't understand that command.*"
    )