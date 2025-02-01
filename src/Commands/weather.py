from telegram import Update
from telegram.ext import ContextTypes
import requests
import logging

from dotenv import load_dotenv
import os

from Tools import send_message

# Load environment variables
load_dotenv(dotenv_path="../.env")
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def Weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await send_message(
            update=update,
            context=context,
            text="Please provide a city name. Usage: `/weather <city>`"
        )
        return

    # OpenWeatherMap API URL
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

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

            # Send weather information to the user via Telegram
            await send_message(
                update=update,
                context=context,
                text=f"""\
🌆 *Weather in {city_name}*
🌤️ Description: *{weather_description}*
🌡️ Temperature: *{temperature}°C*
💧 Humidity: *{humidity}%*
🌬️ Wind Speed: *{wind_speed} m/s*\
"""
            )
        else:
            # If the city is not found
            logging.warning(f"City not found: {city}")
            await send_message(
                update=update,
                context=context,
                text="🚫 *City not found. Please check the city name and try again.*"
            )

    except Exception as e:
        # Handle any exceptions during the API call
        logging.error(f"Error retrieving weather data for {city}: {e}")
        await send_message(
            update=update,
            context=context,
            text="⚠️ *Error occurred while retrieving weather data. Please try again later.*"
        )