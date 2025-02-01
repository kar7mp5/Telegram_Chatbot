import requests
from telegram import Update
from telegram.ext import ContextTypes

from dotenv import load_dotenv
import os

from Tools import text2markdown

load_dotenv(dotenv_path="../.env")
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles weather commands.
    
    Retrieves and shows weather forecast for the specified city.
    
    Args:
        update (Update): Incoming update containing the message.
        context (ContextTypes.DEFAULT_TYPE): Contextual information related to the command.
    """
    # Get the city name from the user input
    if context.args:
        city = " ".join(context.args)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode="MarkdownV2",
            text=text2markdown("Please provide a city name. Usage: `/weather <city>`")
        )
        return

    # OpenWeatherMap API URL
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        # Call the API and get the response
        response = requests.get(url)
        data = response.json()

        print(data)

        # Check if the request was successful
        if response.status_code == 200:
            city_name = data["name"]
            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            # Send weather information to the user via Telegram
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                parse_mode="MarkdownV2",
                text=(
                    text2markdown(f"""\
*Weather in {city_name}*
Description: *{weather_description}*
Temperature: *{temperature}°C*
Humidity: *{humidity}%*
Wind Speed: *{wind_speed} m/s*\
"""
                    )
                )
            )
        else:
            # If the city is not found
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                parse_mode="MarkdownV2",
                text=text2markdown("*City not found. Please check the city name and try again.*")
            )
    except Exception as e:
        # Handle any exceptions during the API call
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode="MarkdownV2",
            text=text2markdown("*Error occurred while retrieving weather data. Please try again later.*")
        )
        print(f"Error: {e}")