import os
import openai
from dotenv import load_dotenv
from colorama import Fore, Style
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI API key
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INSTRUCTIONS = """<<PUT THE PROMPT HERE>>"""

TEMPERATURE = 0.5
MAX_TOKENS = 500
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
MAX_CONTEXT_QUESTIONS = 10  # Limits how many questions we include in the prompt

async def get_response(instructions, previous_questions_and_answers, new_question):
    """Get a response from ChatCompletion API"""
    messages = [
        {"role": "system", "content": instructions},
    ]
    
    # Add previous questions and answers
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": answer})

    # Add the new question
    messages.append({"role": "user", "content": new_question})

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Updated to the latest model
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_p=1,
            frequency_penalty=FREQUENCY_PENALTY,
            presence_penalty=PRESENCE_PENALTY,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error: {e}")
        return "An error occurred while fetching the response."

async def get_moderation(question):
    """Check if the question passes OpenAI's moderation checks"""
    try:
        moderation = await client.moderations.create(input=question)
        result = moderation.results[0]
        if result.flagged:
            flagged_categories = [key for key, value in result.categories.items() if value]
            return flagged_categories
        return None
    except Exception as e:
        logger.error(f"Moderation API Error: {e}")
        return ["Moderation API error"]

async def main():
    os.system("cls" if os.name == "nt" else "clear")
    previous_questions_and_answers = []  # Keep track of the chat history

    while True:
        new_question = input(Fore.GREEN + Style.BRIGHT + "What can I get you?: " + Style.RESET_ALL)

        # Moderation check
        errors = await get_moderation(new_question)
        if errors:
            print(Fore.RED + "Sorry, your question didn't pass the moderation check:" + Style.RESET_ALL)
            for error in errors:
                print(f"- {error}")
            continue

        # Get response from OpenAI API
        response = await get_response(INSTRUCTIONS, previous_questions_and_answers, new_question)

        # Store in history
        previous_questions_and_answers.append((new_question, response))

        # Display the response
        print(Fore.CYAN + Style.BRIGHT + "Here you go: " + Style.NORMAL + response + Style.RESET_ALL)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
