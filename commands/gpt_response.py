# gpt_response.py
from telegram.ext import ContextTypes
from telegram import Update
from openai import OpenAI

from dotenv import load_dotenv
import os


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def gpt_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """GPT response
    
    Args:
        update (Update): Incoming update containing the message.
        context (ContextTypes.DEFAULT_TYPE): Contextual information related to the command.
    
    Returns:
        chat_completion (str): gpt response
    """
    client = OpenAI(
        api_key=OPENAI_API_KEY
    )
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": update.message.text,
            }
        ],
        model="gpt-3.5-turbo",
    ) 

    await update.message.reply_text(chat_completion.choices[0].message.content)
