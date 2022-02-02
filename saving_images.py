import datetime
import imghdr
import os
import time
from os import listdir, path
from pathlib import Path
from urllib.parse import urlparse

import requests
import telegram
from dotenv import load_dotenv

MAX_IMAGE_SIZE = 20971520


def is_image_appropriate(file_path):
    is_image_size_appropriate = os.path.getsize(file_path) < MAX_IMAGE_SIZE
    is_file = path.isfile(file_path)
    is_image = imghdr.what(file_path)
    return is_file and is_image and is_image_size_appropriate


def download_epic_images(nasa_token, images, folder_with_images):
    params = {
        'api_key':  nasa_token,
    }
    for image in images:
        image_name = image['image_name']
        image_date = image['image_date']
        image_url = ('https://api.nasa.gov/EPIC/archive/natural/'
                     f'{image_date}/png/{image_name}.png')
        response = requests.get(image_url,
                                params=params)
        response.raise_for_status()
        Path(folder_with_images).mkdir(parents=True, exist_ok=True)
        image = f'{folder_with_images}/{image_name}.png'
        with open(image, 'wb') as file:
            file.write(response.content)


def send_images_on_tgchat(images_path, bot_token, chat_id, sending_period):
    bot = telegram.Bot(token=bot_token)
    bot.get_updates()
    images_in_dir = listdir(images_path)
    for image in images_in_dir:
        full_image_path = path.join(images_path, image)
        if is_image_appropriate(full_image_path):
            with open(full_image_path, 'rb') as image:
                bot.send_photo(chat_id=chat_id, photo=image)
            time.sleep(int(sending_period))


def parse_image_info(image_date, image_name):
    image_date_format = '%Y-%m-%d %H:%M:%S'
    fetched_date = datetime.datetime.strptime(image_date, image_date_format)
    image_date = fetched_date.strftime("%Y/%m/%d")
    image_info = {'image_date': image_date,
                  'image_name': image_name,
                  }
    return image_info


def get_nasa_images_info(token):
    nasa_url = 'https://api.nasa.gov/EPIC/api/natural/images'
    params = {
        'api_key': token,
    }
    response = requests.get(nasa_url, params)
    images = []
    for image in response.json()[:2]:
        image_info = parse_image_info(image['date'], image['image'])
        images.append(image_info)
    return images


def download_spacex_images(links, images_path, images_amount):
    Path(images_path).mkdir(parents=True, exist_ok=True)
    for num, link in enumerate(links[:images_amount]):
        response = requests.get(link)
        response.raise_for_status()
        image_path = f'{images_path}/spacex{num}.jpg'
        with open(image_path, 'wb') as file:
            file.write(response.content)


def fetch_spacex_last_launch():
    response = requests.get('https://api.spacexdata.com/v3/launches/past')
    response.raise_for_status()
    images = [link for flight in response.json()
              for link in flight['links']['flickr_images']]
    return images


def save_nasa_apod(images_url, image_path):
    Path(image_path).mkdir(parents=True, exist_ok=True)
    for num, image_url in enumerate(images_url):
        response = requests.get(image_url)
        extension = get_extension(image_url)
        image = f'{image_path}/apod{num}{extension}'
        with open(image, 'wb') as file:
            file.write(response.content)


def get_apod_images(token, amount):
    url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'api_key': token,
        'count': amount,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    images = [flight['hdurl'] for flight in response.json() if flight]
    return images


def get_extension(url):
    image_url = urlparse(url)
    filename, file_extension = os.path.splitext(image_url.path)
    return file_extension


def main():
    photos_path = 'space_photos'
    load_dotenv()
    nasa_token = os.environ['NASA_TOKEN']
    nasa_images_amount = int(os.environ.get('NASA_IMAGES_AMOUNT', '3'))
    try:
        nasa_images = get_apod_images(nasa_token, nasa_images_amount)
        save_nasa_apod(nasa_images, photos_path)
        spacex_last_launch_photos = fetch_spacex_last_launch()
        spacex_images_amount = int(os.environ.get('SPACEX_IMAGES_AMOUNT', '2'))
        download_spacex_images(spacex_last_launch_photos,
                               photos_path, spacex_images_amount)
        images = get_nasa_images_info(nasa_token)
        download_epic_images(nasa_token, images, photos_path)
        tg_bot_token = os.environ['TELEGRAM_BOT_TOKEN']
        tg_chat_id = os.environ['TELEGRAM_CHAT_ID']
        sending_period = os.environ.get('SENDING_PERIOD', '86400')
        send_images_on_tgchat(photos_path, tg_bot_token,
                              tg_chat_id, sending_period)
        print('Фотографии отправлены в канал')
    except requests.exceptions.HTTPError:
        print('Проверьте введенную вами ссылку')


if __name__ == '__main__':
    main()
