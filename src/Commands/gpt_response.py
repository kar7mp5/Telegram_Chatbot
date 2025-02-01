from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import openai
from bs4 import BeautifulSoup
import aiohttp

from dotenv import load_dotenv
import os

from Tools import text2markdown

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

# Google Search API Key & Search Engine ID
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX_ID = os.getenv("GOOGLE_CX_ID")
GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
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
        text=text2markdown(text)
    )

async def get_gpt_response(system_prompt: str, user_prompt: str) -> str:
    """
    Generates a response from the GPT API.

    Args:
        system_prompt (str): Instruction for the GPT model.
        user_prompt (str): User's input message.

    Returns:
        str: GPT-generated response.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ GPT response generation error: {e}"

async def fetch_page_content(url: str) -> str:
    """
    Fetches the content of a web page and extracts the main text.

    Args:
        url (str): The URL of the web page.

    Returns:
        str: Extracted text from the page.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")

        # Extract the text from the main content
        # You can customize this to suit the structure of the page
        paragraphs = soup.find_all("p")
        page_text = "\n".join([para.get_text() for para in paragraphs])

        return page_text[:1500]  # Return the first 1000 characters of the content for brevity
    except Exception as e:
        return f"⚠️ 페이지 내용 불러오기 오류: {e}"

async def web_search(query: str) -> str:
    """
    Uses Google Custom Search API to perform a real web search and fetch page content.

    Args:
        query (str): The search query.

    Returns:
        str: Search result with page content.
    """
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX_ID,
        "q": query,
        "num": 1
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GOOGLE_SEARCH_URL, params=params) as resp:
                data = await resp.json()

        if "items" in data:
            results = data["items"]
            output = []
            for res in results:
                title = res['title']
                url = res['link']
                content = await fetch_page_content(url)  # Fetch the content from the page
                output.append(f"""\
# {title}
<link>
{url}
</link>
<content>
{content}
</content>\
""")
            return "\n".join(output)
        else:
            return "No search results found."
    except Exception as e:
        return f"⚠️ Web search error: {e}"

async def gpt_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user messages and generates a GPT response.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    user_prompt = update.message.text
    system_prompt = f"""\
Think step-by-step before responding.
Extract the key topic from the user's question.
<User Question>
{user_prompt}
</User Question>
Respond in Korean.\
"""
    keyword = await get_gpt_response(system_prompt, "Extract keyword")

    # Generate inline buttons for web search confirmation
    keyboard = [
        [
            InlineKeyboardButton("🔎 Yes", callback_data="yes_search"),
            InlineKeyboardButton("❌ No", callback_data="no_search")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(update, context, f"🔍 *'{keyword}'* 에 대한 웹 검색을 진행할까요?")
    context.user_data['question'] = user_prompt
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        parse_mode="MarkdownV2",
        text="검색하시겠습니까?",
        reply_markup=reply_markup
    )

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles inline button responses for web search.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    query = update.callback_query
    await query.answer()

    user_prompt = context.user_data.get('question', '')

    if query.data == "yes_search":
        search_result = await web_search(f"Explain about {user_prompt}")
        print(search_result)
        system_prompt = f"""\
Think step-by-step before responding.
Explain about the following contents:
<Content>
{search_result}
<\Content>
Respond in Korean.\
"""
        search_result = await get_gpt_response(system_prompt, user_prompt)

        response_text = f"🔍 *검색 결과*\n{search_result}"
    else:
        system_prompt = """\
Think step-by-step before responding.
Respond in Korean.\
"""
        response_text = await get_gpt_response(system_prompt, user_prompt)

    await send_message(update, context, response_text)