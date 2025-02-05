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

TEMPERATURE = 0.5
MAX_TOKENS = 500
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
MAX_CONTEXT_QUESTIONS = 10


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
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    # TODO: Add previous questions and answers
    messages.append({"role": "user", "content": user_prompt})

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_p=1,
            frequency_penalty=FREQUENCY_PENALTY,
            presence_penalty=PRESENCE_PENALTY,
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


async def _web_search(query: str) -> list[dict[str, str]]:
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
                output.append({
                    "status": "success",
                    "title": title, 
                    "link": url, 
                    "content": content
                })
            
            logger.info(f"Web search completed with {len(results)} results.")
            return output

        else:
            logger.warning("No search results found.")
            return [{
                "status": "error", 
                "content": "No search results found."
            }]

    except Exception as e:
        logger.error(f"Failed to search content: {e}")
        return [{
            "status": "error", 
            "content": f"⚠️ Fail to search content: {e}"
        }]


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        # Click 'Yes' button
        search_result = await _web_search(f"Explain about {user_prompt}")
        
        if search_result[0]["status"] == "success":      
            system_prompt = f"""\
Follow these structured guidelines using MarkdownV2 parse mode:

*1\. Basic Formatting*  
Use the following styles for emphasis:  
- *bold \*text*  
- _italic \*text_  
- __underline__  
- ~strikethrough~  
- ||spoiler||

*2\. Headings Formatting*  
- Instead of using `#`, `##`, or `###` for headings, always use *bold* formatting to indicate section titles.  
- Example:  
- *Correct:* *Section Title*  
- *Incorrect:* # Section Title

*3\. Links and Mentions*  
- [inline URL](http://www.example.com/)  
- [inline mention of a user](tg://user?id=123456789)  

*4\. Custom Emoji*  
Insert custom emoji like this: ![👍](tg://emoji?id=5368324170671202286)

*5\. Code Blocks*  
- Inline `code` for short snippets  
- ```python
pre\-formatted fixed\-width code block written in the Python programming language
```

*6\. Quotations*  
>Block quotation started  
>Block quotation continued  
**>Expandable block quotation starts here**  
>Hidden content with ||spoiler|| format

*7\. Escaping Characters*  
Escape special characters like \*, \_, \[, \], \(, \), \~, \`, \>, \#, \+, \-, \=, \|, \., \! using a preceding backslash (\\).

*8\. Complex Styling Example*  
*bold _italic bold ~italic bold strikethrough ||italic bold strikethrough spoiler||~ __underline italic bold___ bold*

_Ensure all syntax is properly escaped to avoid formatting errors in the final output._

Explain about the following contents:
<Content>{search_result[0]['content']}</Content>

Think step-by-step before responding.
Response by the following format:
<response>
"""
            gpt_response = await _get_gpt_response(system_prompt, user_prompt)
            response_text = f"🔍 *Search result*\n{gpt_response}"
        else:
            system_prompt = """
Follow these structured guidelines using MarkdownV2 parse mode:

*1\. Basic Formatting*  
Use the following styles for emphasis:  
- *bold \*text*  
- _italic \*text_  
- __underline__  
- ~strikethrough~  
- ||spoiler||

*2\. Headings Formatting*  
- Instead of using `#`, `##`, or `###` for headings, always use *bold* formatting to indicate section titles.  
- Example:  
- *Correct:* *Section Title*  
- *Incorrect:* # Section Title

*3\. Links and Mentions*  
- [inline URL](http://www.example.com/)  
- [inline mention of a user](tg://user?id=123456789)  

*4\. Custom Emoji*  
Insert custom emoji like this: ![👍](tg://emoji?id=5368324170671202286)

*5\. Code Blocks*  
- Inline `code` for short snippets  
- ```python
pre\-formatted fixed\-width code block written in the Python programming language
```

*6\. Quotations*  
>Block quotation started  
>Block quotation continued  
**>Expandable block quotation starts here**  
>Hidden content with ||spoiler|| format

*7\. Escaping Characters*  
Escape special characters like \*, \_, \[, \], \(, \), \~, \`, \>, \#, \+, \-, \=, \|, \., \! using a preceding backslash (\\).

*8\. Complex Styling Example*  
*bold _italic bold ~italic bold strikethrough ||italic bold strikethrough spoiler||~ __underline italic bold___ bold*

_Ensure all syntax is properly escaped to avoid formatting errors in the final output._

Think step-by-step before responding."""
            response_text = await _get_gpt_response(system_prompt, user_prompt)
    else:
        # Click 'No' button
        system_prompt = """
Follow these structured guidelines using MarkdownV2 parse mode:

*1\. Basic Formatting*  
Use the following styles for emphasis:  
- *bold \*text*  
- _italic \*text_  
- __underline__  
- ~strikethrough~  
- ||spoiler||

*2\. Headings Formatting*  
- Instead of using `#`, `##`, or `###` for headings, always use *bold* formatting to indicate section titles.  
- Example:  
  - *Correct:* *Section Title*  
  - *Incorrect:* # Section Title

*3\. Links and Mentions*  
- [inline URL](http://www.example.com/)  
- [inline mention of a user](tg://user?id=123456789)  

*4\. Custom Emoji*  
Insert custom emoji like this: ![👍](tg://emoji?id=5368324170671202286)

*5\. Code Blocks*  
- Inline `code` for short snippets  
- ```python
pre\-formatted fixed\-width code block written in the Python programming language
```

*6\. Quotations*  
>Block quotation started  
>Block quotation continued  
**>Expandable block quotation starts here**  
>Hidden content with ||spoiler|| format

*7\. Escaping Characters*  
Escape special characters like \*, \_, \[, \], \(, \), \~, \`, \>, \#, \+, \-, \=, \|, \., \! using a preceding backslash (\\).

*8\. Complex Styling Example*  
*bold _italic bold ~italic bold strikethrough ||italic bold strikethrough spoiler||~ __underline italic bold___ bold*

_Ensure all syntax is properly escaped to avoid formatting errors in the final output._

Think step-by-step before responding."""
        response_text = await _get_gpt_response(system_prompt, user_prompt)

    logger.info(f"Sending callback response to '{user.username}' (ID: {user.id}): {response_text[:50]}...")

    await send_message(update=update, context=context, text=response_text)


async def gpt_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user messages and generates a GPT response.

    Args:
        update (Update): Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    user = update.effective_user
    user_prompt = update.message.text.replace("/gpt", "") # Exception of command keyword

    logger.info(f"Received GPT request from '{user.username}' (ID: {user.id}): {user_prompt}")

    if not user_prompt.strip():
        # Exception of the blank response
        logger.warning(f"Empty GPT request from '{user.username}' (ID: {user.id})")
        await send_message(update=update, 
                           context=context, 
                           text="⚠️ Please provide a valid question.")
        return

    system_prompt = """\
Think step-by-step before responding.
Extract the key topic (max 30 chars).
Format:
Key_topic"""
    keyword = await _get_gpt_response(system_prompt, user_prompt)

    logger.info(f"Extracted keyword '{keyword}' from '{user.username}' (ID: {user.id})")

    keyboard = [
        [InlineKeyboardButton("🔎 Yes", callback_data="yes_search"),
         InlineKeyboardButton("❌ No", callback_data="no_search")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['question'] = user_prompt

    await send_message(update=update, 
                       context=context, 
                       text=f"🔍 Search for `{keyword}`?", 
                       reply_markup=reply_markup)