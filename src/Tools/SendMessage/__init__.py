from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from Tools import text2markdown

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup: ReplyKeyboardMarkup = None):
    """
    Sends a message to the Telegram chat in MarkdownV2 format.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
        text (str): Message content.
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode="MarkdownV2",
        text=text2markdown(text),
        reply_markup=reply_markup
    )