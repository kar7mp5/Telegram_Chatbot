from telegram import Update
from telegram.ext import ContextTypes
from tools import send_message

async def Help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles help commands.
    
    Explain about telegram bot's handlers.

    Args:
        update (Update): Incoming update containing the message.
        context (ContextTypes.DEFAULT_TYPE): Contextual information related to the command.
    """
    await send_message(
        update=update,
        context=context,
        text="""\
`/help` - Show all commands
`/weather <city>` - Show weather forecast for the specified city
`/gpt <prompt>` - Ask GPT a question
"""
    )
