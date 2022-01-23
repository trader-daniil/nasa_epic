import datetime
import os
import time
from os import listdir, path
from pathlib import Path
import requests
import telegram
from dotenv import load_dotenv


def downloading_epic_image(token, image_info, folder):
    params = {
        'api_key':  token,
    }
    image_date = image_info['image_date']
    image_name = image_info['image_name']
    image_url = ('https://api.nasa.gov/EPIC/archive/natural/'
                 f'{image_date}/png/{image_name}.png')
    response = requests.get(image_url,
                            params=params)
    response.raise_for_status()
    Path(folder).mkdir(parents=True, exist_ok=True)
    image = f'{folder}/{image_name}.png'
    with open(image, 'wb') as file:
        file.write(response.content)


def sending_images():
    bot = telegram.Bot(token=BOT_TOKEN)
    bot.get_updates()
    my_path = 'epics'
    contain = listdir(my_path)
    for el in contain:
        el_path = path.join(my_path, el)
        if path.isfile(el_path) and el.endswith('.png'):
            with open(el_path, 'rb') as image:
                bot.send_photo(chat_id=CHAT_ID, photo=image)
                time.sleep(int(SENDING_PERIOD))


def parsing_image_info(epic):
    image_date = datetime.date.fromisoformat(epic['date'][:10])
    image_date = image_date.strftime("%Y/%m/%d")
    image_name = epic['image']
    image_info = {'image_date': image_date,
                  'image_name': image_name,
                  }
    return image_info


def getting_image_info(token, url, folder_name):
    params = {
        'api_key': token,
    }
    response = requests.get(url, params)
    for image in response.json()[:3]:
        image_info = parsing_image_info(image)
        downloading_epic_image(token, image_info, folder_name)
    return sending_images()


def main():
    load_dotenv()
    AUTH_TOKEN = os.environ['AUTH_TOKEN']
    NASA_URL = 'https://api.nasa.gov/EPIC/api/natural/images'
    try:
        getting_image_info(AUTH_TOKEN, NASA_URL, 'epics')
        print('Фотографии отправлены в канал')
    except requests.exceptions.HTTPError:
        print('Проверьте введенную вами ссылку')


if __name__ == '__main__':
    load_dotenv()
    CHAT_ID = os.environ['CHAT_ID']
    BOT_TOKEN = os.environ['BOT_TOKEN']
    try:
        SENDING_PERIOD = os.environ['SENDING_PERIOD']
    except KeyError:
        SENDING_PERIOD = '86400'
    main()
