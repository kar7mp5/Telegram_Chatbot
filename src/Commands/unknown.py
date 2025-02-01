from telegram import Update
from telegram.ext import ContextTypes
from Tools import text2markdown

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles unknown commands.

    Sends a message to the user indicating that the command was not understood.

    Args:
        update (Update): Incoming update containing the message.
        context (ContextTypes.DEFAULT_TYPE): Contextual information related to the command.
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode="MarkdownV2",
        text=text2markdown("*Sorry, I didn't understand that command.*")
    )
