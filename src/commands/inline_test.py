from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from tools import send_message, setup_logger
import logging

# Initialize the logger configuration
setup_logger()
logger = logging.getLogger(__name__)

# Sample data to paginate
info_list = ["Info 1", "Info 2", "Info 3", "Info 4", "Info 5"]

async def test_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user messages and generates a simple test response with inline buttons for navigation.
    """
    user = update.effective_user
    message = update.message.text

    logger.info(f"Received message from '{user.username}' (ID: {user.id}): {message}")

    # Set the initial index only if not already set
    if 'current_index' not in context.user_data:
        context.user_data['current_index'] = 0  # Start with the first item

    await send_message_with_navigation(update, context, context.user_data['current_index'])

async def send_message_with_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int):
    """
    Sends a message with navigation buttons to move through the information list.
    """
    text = info_list[index]

    keyboard = [
        [
            InlineKeyboardButton("⬅️", callback_data="test_prev"),
            InlineKeyboardButton(f"{index + 1}/{len(info_list)}", callback_data="test_current"),
            InlineKeyboardButton("➡️", callback_data="test_next")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Edit the message if it already exists, otherwise send a new one
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=f"{text}",
            reply_markup=reply_markup
        )
    else:
        await send_message(
            update=update,
            context=context,
            text=f"{text}",
            reply_markup=reply_markup
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles button clicks to navigate through the information list.
    """
    query = update.callback_query
    await query.answer()

    # Ensure only test-related callback data is processed
    if not query.data.startswith("test_"):
        return

    # Ensure the index is initialized
    index = context.user_data.get('current_index', 0)

    # Navigation logic
    if query.data == "test_prev" and index > 0:
        index -= 1
    elif query.data == "test_next" and index < len(info_list) - 1:
        index += 1

    # Update the index
    context.user_data['current_index'] = index

    # Send updated message
    await send_message_with_navigation(update, context, index)