from telegram import Update
from telegram.ext import ContextTypes
from tools import send_message

async def Unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles unknown commands.

    Sends a message to the user indicating that the command was not understood.

    Args:
        update (Update): Incoming update containing the message.
        context (ContextTypes.DEFAULT_TYPE): Contextual information related to the command.
    """
    await send_message(
        update=update,
        context=context,
        text="*Sorry, I didn't understand that command.*"
    )