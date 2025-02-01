from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import openai
from bs4 import BeautifulSoup
import aiohttp

from dotenv import load_dotenv
import os

from tools import send_message

# Load environment variables
# - OpenAI API key
# - Google API key
# - Google CX ID
# - Google Search url
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX_ID = os.getenv("GOOGLE_CX_ID")
GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"


client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)


async def _get_gpt_response(system_prompt: str, user_prompt: str) -> str:
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

async def _fetch_page_content(url: str) -> str:
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
        paragraphs = soup.find_all("p")
        page_text = "\n".join([para.get_text() for para in paragraphs])

        return page_text[:1500]  # TODO: Change this to be parameter

    except Exception as e:
        return f"⚠️ Fail to load page content: {e}"

async def _web_search(query: str) -> str:
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
                content = await _fetch_page_content(url)
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
        return f"⚠️ Fail to search content: {e}"


async def Handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles inline button responses for web search.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    # Get updated answer
    query = update.callback_query
    await query.answer()

    user_prompt = context.user_data.get('question', '')

    if query.data == "yes_search":
        # Click 'Yes'
        search_result = await _web_search(f"Explain about {user_prompt}")

        system_prompt = f"""\
Think step-by-step before responding.
Explain about the following contents:
<Content>
{search_result}
<\Content>
Respond in Korean.\
"""
        search_result = await _get_gpt_response(system_prompt, user_prompt)

        response_text = f"🔍 *검색 결과*\n{search_result}"
    else:
        # Click 'No'
        system_prompt = """\
Think step-by-step before responding.
Respond in Korean.\
"""
        response_text = await _get_gpt_response(system_prompt, user_prompt)

    await send_message(
        update=update, 
        context=context, 
        text=response_text
    )


async def GPT_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user messages and generates a GPT response.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    # Extract the key topic from user's question
    user_prompt = update.message.text
    system_prompt = f"""\
Think step-by-step before responding.
Extract the key topic from the user's question.
<User Question>
{user_prompt}
</User Question>
Respond in Korean.\
"""
    keyword = await _get_gpt_response(system_prompt, "Extract keyword")

    # Generate inline buttons for web search confirmation
    keyboard = [
        [
            InlineKeyboardButton("🔎 Yes", callback_data="yes_search"),
            InlineKeyboardButton("❌ No", callback_data="no_search")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a message to the user instructing them to search for this keyword
    await send_message(
        update=update, 
        context=context, 
        text=f"🔍 *'{keyword}'* 에 대한 웹 검색을 진행할까요?"
    )

    context.user_data['question'] = user_prompt
    
    await send_message(
        update=update, 
        context=context, 
        text="*검색하시겠습니까?*",
        reply_markup=reply_markup
    )