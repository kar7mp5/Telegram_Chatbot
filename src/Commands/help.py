from telegram import Update
from telegram.ext import ContextTypes
from Tools import text2markdown

description = """\
`/help` - Show all commands
`/weather <city>` - Show weather forecast for the specified city
`/gpt <prompt>` - Ask GPT a question
"""


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles help commands.
    
    Explain about telegram bot's handlers.

    Args:
        update (Update): Incoming update containing the message.
        context (ContextTypes.DEFAULT_TYPE): Contextual information related to the command.
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode="MarkdownV2",
        text=text2markdown(description)
    )
