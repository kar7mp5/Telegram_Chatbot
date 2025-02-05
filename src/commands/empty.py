from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application
from tools import send_message, setup_logger
import logging

setup_logger()
logger = logging.getLogger(__name__)

async def _delete_messages(context, chat_id, message_id):
    """
    Function to delete messages synchronously.
    Stops when there are no more messages to delete.
    """
    try:
        for msg_id in range(message_id, message_id - 100, -1):
            if msg_id > 0:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                except Exception as e:
                    # Stop deleting if message no longer exists
                    if "message to delete not found" in str(e).lower():
                        logger.info(f"No more messages to delete after message ID {msg_id}.")
                        break
                    logger.debug(f"Skipping message ID {msg_id}: {e}")
        logger.info(f"Cleared recent chat history for chat ID: {chat_id}")
    except Exception as e:
        logger.warning(f"Could not clear chat history for chat ID: {chat_id}: {e}")

async def empty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the `/empty` command.

    Deletes all previous messages in the chat synchronously
    and logs the interaction, including user and chat details.

    TODO: Implement functionality to also delete chat history from the database.

    Args:
        update (Update): Incoming update containing the message from the user.
        context (ContextTypes.DEFAULT_TYPE): Provides context for the update,
                                              including message metadata.
    """
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Log the empty command request
    logger.info(f"Empty command requested by user '{user.username}' (ID: {user.id}) in chat ID: {chat_id}")

    # Synchronously delete messages
    message_id = update.message.message_id
    await _delete_messages(context, chat_id, message_id)

    await send_message(
        update=update,
        context=context,
        text="Chat history has been cleared."
    )