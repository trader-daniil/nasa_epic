from dotenv import load_dotenv
import telegram
import os

load_dotenv()
BOT_TOKEN = os.environ['BOT_TOKEN']
bot = telegram.Bot(token=BOT_TOKEN)
updates = bot.get_updates()
bot.send_message(text='new bot message', chat_id='@nasa_epic_channel')
