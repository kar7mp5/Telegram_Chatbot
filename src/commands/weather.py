from telegram import Update
from telegram.ext import ContextTypes

import requests
from dotenv import load_dotenv
import logging
import os

from tools import send_message, setup_logger

# Load environment variables
load_dotenv(dotenv_path="../.env")
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# Initialize the logger configuration
setup_logger()
logger = logging.getLogger(__name__)


async def Weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the `/weather` command in Telegram.

    Retrieves real-time weather data for the specified city using the OpenWeatherMap API
    and sends the weather information back to the user.

    Args:
        update (Update): Incoming update containing the message from the user.
        context (ContextTypes.DEFAULT_TYPE): Provides context for the update, 
                                             including arguments and metadata.

    Logging:
        - INFO: When a weather request is received or successfully processed.
        - WARNING: When a city is not found or user provides no city name.
        - ERROR: When an error occurs during the API call or data processing.
    """
    # Get the city name from the user input
    if context.args:
        city = " ".join(context.args)
        logger.info(f"Received weather request for city: {city}")
    else:
        warning_message = "No city provided by the user. Prompting for input."
        logger.warning(warning_message)

        await send_message(
            update=update,
            context=context,
            text="Please provide a city name. Usage: `/weather <city>`"
        )
        return

    # OpenWeatherMap API URL
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    logger.debug(f"API Request URL: {url}")  # Debug log to track the API URL

    try:
        # Call the API and get the response
        response = requests.get(url)
        data = response.json()

        # Check if the request was successful
        if response.status_code == 200:
            city_name = data["name"]
            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            logger.info(f"Successfully retrieved weather data for {city_name}")

            # Send weather information to the user via Telegram
            await send_message(
                update=update,
                context=context,
                text=f"""\n
🌆 *Weather in {city_name}*
🌤️ Description: *{weather_description}*
🌡️ Temperature: *{temperature}°C*
💧 Humidity: *{humidity}%*
🌬️ Wind Speed: *{wind_speed} m/s*
"""
            )
        else:
            # If the city is not found
            logger.warning(f"City not found: {city} (Status Code: {response.status_code})")
            await send_message(
                update=update,
                context=context,
                text="🚫 *City not found. Please check the city name and try again.*"
            )

    except Exception as e:
        # Handle any exceptions during the API call
        logger.error(f"Error retrieving weather data for {city}: {e}")
        await send_message(
            update=update,
            context=context,
            text="⚠️ *Error occurred while retrieving weather data. Please try again later.*"
        )