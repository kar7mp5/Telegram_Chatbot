from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import openai
from bs4 import BeautifulSoup
import aiohttp

from dotenv import load_dotenv
import os
import logging
from tools import send_message, setup_logger

# Initialize the logger configuration
setup_logger()
logger = logging.getLogger(__name__)

# Load environment variables
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
    logger.info(f"Generating GPT response for prompt: {user_prompt}")
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        logger.info("GPT response generated successfully.")
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"GPT response generation error: {e}")
        return f"⚠️ GPT response generation error: {e}"


async def _fetch_page_content(url: str) -> str:
    """
    Fetches the content of a web page and extracts the main text.

    Args:
        url (str): The URL of the web page.

    Returns:
        str: Extracted text from the page.
    """
    logger.info(f"Fetching page content from URL: {url}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        paragraphs = soup.find_all("p")
        page_text = "\n".join([para.get_text() for para in paragraphs])

        logger.info(f"Successfully fetched content from {url}")
        return page_text[:1500]

    except Exception as e:
        logger.error(f"Failed to load page content from {url}: {e}")
        return f"⚠️ Fail to load page content: {e}"


async def _web_search(query: str) -> list[str]:
    """
    Uses Google Custom Search API to perform a real web search and fetch page content.

    Args:
        query (str): The search query.

    Returns:
        list[str]: List of search results with page content.
    """
    logger.info(f"Performing web search for query: {query}")
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX_ID,
        "q": query,
        "num": 5
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
                output.append(f"""\n# {title}\n<link>{url}</link>\n<content>{content}</content>""")
            
            logger.info(f"Web search completed with {len(results)} results.")
            return output

        else:
            logger.warning("No search results found.")
            return ["No search results found."]

    except Exception as e:
        logger.error(f"Failed to search content: {e}")
        return [f"⚠️ Fail to search content: {e}"]


async def Handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles inline button responses for web search.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    user_prompt = context.user_data.get('question', '')

    logger.info(f"Callback query '{query.data}' received from '{user.username}' (ID: {user.id})")

    if query.data == "yes_search":
        search_result = await _web_search(f"Explain about {user_prompt}")
        system_prompt = f"""Think step-by-step before responding.\nExplain about the following contents:\n<Content>{search_result[0]}</Content>"""
        gpt_response = await _get_gpt_response(system_prompt, user_prompt)
        response_text = f"🔍 *Search result*\n{gpt_response}"
    else:
        system_prompt = "Think step-by-step before responding."
        response_text = await _get_gpt_response(system_prompt, user_prompt)

    logger.info(f"Sending callback response to '{user.username}' (ID: {user.id}): {response_text[:50]}...")

    await send_message(update=update, context=context, text=response_text)


async def GPT_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user messages and generates a GPT response.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    user = update.effective_user
    user_prompt = update.message.text

    logger.info(f"Received GPT request from '{user.username}' (ID: {user.id}): {user_prompt}")

    if not user_prompt.replace("/gpt", "").strip():
        # Except the blank response
        logger.warning(f"Empty GPT request from '{user.username}' (ID: {user.id})")
        await send_message(update=update, context=context, text="⚠️ Please provide a valid question.")
        return

    system_prompt = f"""Think step-by-step before responding.\nExtract the key topic from the user's question.\n<User Question>user_prompt</User Question>\nRespond in Korean."""
    keyword = await _get_gpt_response(system_prompt, user_prompt)

    logger.info(f"Extracted keyword '{keyword}' from '{user.username}' (ID: {user.id})")

    keyboard = [
        [InlineKeyboardButton("🔎 Yes", callback_data="yes_search"),
         InlineKeyboardButton("❌ No", callback_data="no_search")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(update=update, context=context, text=f"🔍 Search for *'{keyword}'*?")
    context.user_data['question'] = user_prompt

    await send_message(update=update, context=context, text="*Search?*", reply_markup=reply_markup)