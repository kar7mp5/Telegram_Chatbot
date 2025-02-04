from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from tools import text2markdown

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup: ReplyKeyboardMarkup = None):
    """
    Sends a message to the Telegram chat, optionally formatted in MarkdownV2.

    Args:
        update (Update): Telegram update object, containing message and chat details.
        context (ContextTypes.DEFAULT_TYPE): Context for the bot, providing access to the bot instance.
        text (str): The message content to be sent.
        reply_markup (ReplyKeyboardMarkup, optional): Keyboard layout for custom reply options in the chat.
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode="MarkdownV2",
        text=text2markdown(text),
        reply_markup=reply_markup
    )