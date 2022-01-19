from dotenv import load_dotenv
import telegram
import os

load_dotenv()
CHAT_ID = '@nasa_epic_channel'
BOT_TOKEN = os.environ['BOT_TOKEN']
bot = telegram.Bot(token=BOT_TOKEN)
updates = bot.get_updates()
#bot.send_message(text='new bot message', chat_id=CHAT_ID)

with open('epics/epic_1b_20220117005515.png', 'rb') as image:
    bot.send_photo(chat_id=CHAT_ID, photo=image)

