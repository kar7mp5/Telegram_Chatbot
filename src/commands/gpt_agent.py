from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import openai
from bs4 import BeautifulSoup
import aiohttp
from dotenv import load_dotenv
import logging
import os

from tools import send_message, setup_logger, load_prompt
from databases import init_user_db, save_message, load_messages

class GPT_Agent:
    """
    A class representing a GPT-based AI agent for handling requests.

    This class initializes the API configuration, environment variables,
    and system prompts required for interacting with OpenAI's API.
    """

    # Initialize the logger configuration
    setup_logger()
    logger = logging.getLogger(__name__)

    # Load environment variables
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CX_ID = os.getenv("GOOGLE_CX_ID")
    GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

    # GPT setting environment variables
    TEMPERATURE = 0.5
    MAX_TOKENS = 500
    FREQUENCY_PENALTY = 0
    PRESENCE_PENALTY = 0.6
    MAX_CONTEXT_QUESTIONS = 10

    # Scraping limitation.
    PAGE_LIMIT = 1500

    # Initiaulize chat history databases
    init_user_db()

    # Load system prompts
    _base_path: str = os.path.join(os.getcwd(), "src/prompts")
    MAKRDOWN_PROMPT: str = load_prompt(os.path.join(_base_path, "telegram_markdownV2.txt"))
    KEYWORD_PROMPT: str = load_prompt(os.path.join(_base_path, "keyword_extraction.txt"))

    def __init__(self):
        """
        Initializes the GPT_Agent instance.

        This constructor ensures that the OpenAI API key is available and
        sets up the OpenAI API client.

        Raises:
            ValueError: If the OpenAI API key is not found in the environment variables.
        """
        if not self.OPENAI_API_KEY:
            self.logger.error("OPENAI_API_KEY is not set in the environment variables.")
            raise ValueError("Missing OpenAI API Key")

        self.client = openai.AsyncOpenAI(api_key=self.OPENAI_API_KEY)
        self.logger.info("GPT_Agent initialized successfully.")

    async def _get_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates a response from the GPT API.

        Args:
            system_prompt (str): Instruction for the GPT model.
            user_prompt (str): User's input message.

        Returns:
            str: GPT-generated response.
        """
        self.logger.info(f"Generating GPT response for prompt")

        messages = [
            {"role": "system", "content": system_prompt}
        ]
        # TODO: Add previous questions and answers
        messages.append({"role": "user", "content": user_prompt})

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
                top_p=1,
                frequency_penalty=self.FREQUENCY_PENALTY,
                presence_penalty=self.PRESENCE_PENALTY,
            )
            self.logger.info("GPT response generated successfully.")
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"GPT response generation error: {e}")
            return f"⚠️ GPT response generation error: {e}"

    async def _get_response_chat_history(self, system_prompt: str, user_prompt: str, user_id: int, username: str) -> str:
        """
        Generates a response from the GPT API, including previous chat history.

        Args:
            system_prompt (str): Instruction for the GPT model.
            user_prompt (str): User's new input message.
            user_id (int): Unique identifier of the user.
            username (str): Telegram username of the user.

        Returns:
            str: GPT-generated response.
        """
        self.logger.info(f"Generating GPT response for user ({username}): {user_prompt}")

        # Fetch previous chat history from the database
        chat_history = load_messages(user_id, username)
        
        # Prepare message format for GPT API
        messages = [{"role": "system", "content": system_prompt}]

        # Process chat history and add it as context
        previous_questions_and_answers = []
        for record in chat_history[-self.MAX_CONTEXT_QUESTIONS:]:  # Keep only the most recent context messages
            question, sender, message, timestamp = record
            if sender == "user":
                previous_questions_and_answers.append({"role": "user", "content": message})
            elif sender == "bot":
                previous_questions_and_answers.append({"role": "assistant", "content": message})

        # Append processed history
        messages.extend(previous_questions_and_answers)

        # Append new user question
        messages.append({"role": "user", "content": user_prompt})

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
                top_p=1,
                frequency_penalty=self.FREQUENCY_PENALTY,
                presence_penalty=self.PRESENCE_PENALTY,
            )
            self.logger.info("GPT response generated successfully.")
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"GPT response generation error: {e}")
            return f"⚠️ GPT response generation error: {e}"

    async def _fetch_page_content(self, url: str) -> str:
        """
        Fetches the content of a web page and extracts the main text.

        Args:
            url (str): The URL of the web page.

        Returns:
            str: Extracted text from the page.
        """
        self.logger.info(f"Fetching page content from URL: {url}")
        try:
            async with aiohttp.self.clientSession() as session:
                async with session.get(url) as resp:
                    html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")
            paragraphs = soup.find_all("p")
            page_text = "\n".join([para.get_text() for para in paragraphs])

            self.logger.info(f"Successfully fetched content from {url}")
            return page_text[:self.PAGE_LIMIT]
        except Exception as e:
            self.logger.error(f"Failed to load page content from {url}: {e}")
            return f"⚠️ Fail to load page content: {e}"

    async def _web_search(self, query: str) -> list[dict[str, str]]:
        """
        Uses Google Custom Search API to perform a real web search and fetch page content.

        Args:
            query (str): The search query.

        Returns:
            list[dict[str, str]]: Search results with page content.
        """
        self.logger.info(f"Performing web search for query: {query}")
        params = {
            "key": self.GOOGLE_API_KEY,
            "cx": self.GOOGLE_CX_ID,
            "q": query,
            "num": 5
        }

        try:
            async with aiohttp.self.clientSession() as session:
                async with session.get(self.GOOGLE_SEARCH_URL, params=params) as resp:
                    data = await resp.json()

            if "items" in data:
                results = data["items"]
                output = []
                for res in results:
                    title = res['title']
                    url = res['link']
                    content = await self._fetch_page_content(url)
                    output.append({
                        "status": "success",
                        "title": title, 
                        "link": url, 
                        "content": content
                    })

                self.logger.info(f"Web search completed with {len(results)} results.")
                return output
            else:
                self.logger.warning("No search results found.")
                return [{
                    "status": "error", 
                    "content": "No search results found."
                }]
        except Exception as e:
            self.logger.error(f"Failed to search content: {e}")
            return [{
                "status": "error", 
                "content": f"⚠️ Fail to search content: {e}"
            }]

    async def gpt_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles user messages and generates a GPT response.

        Args:
            update (Update): Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
        """
        user = update.effective_user
        user_prompt = update.message.text.replace("/gpt", "") # Exception of command keyword
        
        self.logger.info(f"Received GPT request from '{user.username}' (ID: {user.id}): {user_prompt}")

        # Exception of the blank response
        if not user_prompt.strip():
            self.logger.warning(f"Empty GPT request from '{user.username}' (ID: {user.id})")
            await send_message(update=update, context=context, text="⚠️ Please provide a valid question.")
            return

        response_text: str = await self._get_response(self.MAKRDOWN_PROMPT, user_prompt)

        self.logger.info(f"Sending callback response to '{user.username}' (ID: {user.id}): {response_text[:50]}...")
        await send_message(update=update, context=context, text=response_text)

    async def search_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles user messages and generates a GPT response.

        Args:
            update (Update): Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
        """
        user = update.effective_user
        user_prompt = update.message.text.replace("/search", "") # Exception of command keyword
        
        self.logger.info(f"Received GPT request from '{user.username}' (ID: {user.id}): {user_prompt}")

        # Exception of the blank response
        if not user_prompt.strip():
            self.logger.warning(f"Empty GPT request from '{user.username}' (ID: {user.id})")
            await send_message(update=update, context=context, text="⚠️ Please provide a valid question.")
            return

        keyword: str = await self._get_response(self.KEYWORD_PROMPT, user_prompt)

        self.logger.info(f"Extracted keyword '{keyword}' from '{user.username}' (ID: {user.id})")

        keyboard = [[
            InlineKeyboardButton("🔎 Yes", callback_data="gpt_yes_search"),
            InlineKeyboardButton("❌ No", callback_data="gpt_no_search")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['question'] = user_prompt

        await send_message(
            update=update, 
            context=context, 
            text=f"🔍 Search for `{keyword}`?", 
            reply_markup=reply_markup
        )

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

        self.logger.info(f"Callback query '{query.data}' received from '{user.username}' (ID: {user.id})")

        # Click 'Yes' button
        if query.data == "gpt_yes_search":
            search_result = await self._web_search(f"Explain about {user_prompt}")

            # Success for web searching
            if search_result[0]["status"] == "success":
                system_prompt: str = f"""\
{self.MAKRDOWN_PROMPT}
Explain about the following contents:
<Content>{search_result[0]['content']}</Content>

Think step-by-step before responding.
Response by the following format:
<response>
"""
                gpt_response = await self._get_response_chat_history(system_prompt, user_prompt, user.id, user.username)
                response_text = f"🔍 *Search result*\n{gpt_response}"
            # Fail to web searching
            elif search_result[0]["status"] == "error":
                system_prompt: str = f"""\
{self.MAKRDOWN_PROMPT}
Think step-by-step before responding.
"""
                response_text = await self._get_response_chat_history(system_prompt, user_prompt, user.id, user.username)
        # Click 'No' button
        else:
            system_prompt: str = f"""\
{self.MAKRDOWN_PROMPT}
Think step-by-step before responding.
"""
            response_text = await self._get_response_chat_history(system_prompt, user_prompt, user.id, user.username)

        # Save chat history
        save_message(user.id, user.username, "user", user_prompt)
        save_message(user.id, user.username, "bot", response_text)
        self.logger.info(f"Sending callback response to '{user.username}' (ID: {user.id}): {response_text[:50]}...")

        await send_message(update=update, context=context, text=response_text)