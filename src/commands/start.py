from telegram import Update
from telegram.ext import ContextTypes
from tools import send_message

async def Start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the bot

    Args:
        update (Update): Incoming update containing the message.
        context (ContextTypes.DEFAULT_TYPE): Contextual information related to the command.
    """
    await send_message(
        update=update,
        context=context,
        text="*I'm a bot, please talk to me!*"
    )