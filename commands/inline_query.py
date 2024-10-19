# inline_query.py
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes
from uuid import uuid4

import random


async def getAdvice():
    # Hardcoded advice for demonstration; replace with file reading if needed.
    advice_list = [
        "Stay positive!",
        "Keep learning.",
        "Embrace challenges.",
        "Believe in yourself.",
        "Take breaks.",
    ]
    # Return a random piece of advice.
    return random.choice(advice_list)


async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    advice_message = await getAdvice()  # Await the asynchronous function
    await context.bot.send_message(chat_id=update.effective_chat.id, text=advice_message)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if query:
        # 예를 들어, 'advice'라는 쿼리에 반응
        if query.lower() == "advice":
            advice_message = await getAdvice()  # 랜덤 조언 가져오기
            results = [
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="Get Random Advice",
                    input_message_content=InputTextMessageContent(advice_message)
                )
            ]
            await update.inline_query.answer(results)
        else:
            results = [
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="Echo: " + query,
                    input_message_content=InputTextMessageContent(query)
                )
            ]
            await update.inline_query.answer(results)
