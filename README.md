# Telegram_Chatbot
Telegram Chatbot  

The Telegram bot was created by referring to the [official docs](https://docs.python-telegram-bot.org/en/v21.6/).  

### Table of Contents

[Install Libraries](#install-libraries)  
[Quick Start](#quick-start)  
[File Structure](#file-structure)  
[Telegram MarkdownV2 style](#telegram-markdownv2-style)

---
### Install Libraries

```bash
$ pip3 install -r requirements.txt
```

---
### Quick Start
> **Environment Variables**  
```
BOT_TOKEN=<Telegram-Bot-API-KEY>
OPENWEATHERMAP_API_KEY=<OpenWeatherMap-API-KEY>
```

> **Setup Telegram Bot**  
[Tutorial Docs](https://core.telegram.org/bots/tutorial) 

Creating a new bot  
Use the `/newbot` command to create a new bot. [@BotFather](https://t.me/botfather) will ask you for a name and username, then generate an authentication token for your new bot.  

- The **name** of your bot is displayed in contact details and elsewhere.  

- The **username** is a short name, used in search, mentions and t.me links. Usernames are 5-32 characters long and not case sensitive – but may only include Latin characters, numbers, and underscores. Your bot's username must end in 'bot’, like 'tetris_bot' or 'TetrisBot'.  

- The **token** is a string, like `110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`, which is required to authorize the bot and send requests to the Bot API. Keep your token secure and store it safely, it can be used by anyone to control your bot.  
  
> **Setup OpenWeather Map**  
[OpenWeather API Docs](https://openweathermap.org/)  


**Run bot**
```bash
$ python3 bot.py
```

---
### File Structure 

```
├── commands/          # Telegram bot commands
│   ├── __init__.py
│   ├── start.py
│   ├── unknown.py
│   └── inline_query.py
│
└── .env # Telegram bot API key
```

---
### Telegram MarkdownV2 style

[Official docs](https://core.telegram.org/bots/api#markdownv2-style)  
