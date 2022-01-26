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


def check_if_image(file_path):
    return (path.isfile(file_path) and imghdr.what(file_path)
            and int(os.path.getsize(file_path)) < 20971520)


def download_epic_image(token, image_info, folder):
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


def send_images(images_path):
    load_dotenv()
    BOT_TOKEN = os.environ['BOT_TOKEN']
    CHAT_ID = os.environ['CHAT_ID']
    SENDING_PERIOD = os.environ.get('SENDING_PERIOD', '86400')
    bot = telegram.Bot(token=BOT_TOKEN)
    bot.get_updates()
    files_in_dir = listdir(images_path)
    for file in files_in_dir:
        el_path = path.join(images_path, file)
        if check_if_image(el_path):
            with open(el_path, 'rb') as image:
                bot.send_photo(chat_id=CHAT_ID, photo=image)
            time.sleep(int(SENDING_PERIOD))


def parse_image_info(epic):
    image_date = datetime.date.fromisoformat(epic['date'][:10])
    image_date = image_date.strftime("%Y/%m/%d")
    image_name = epic['image']
    image_info = {'image_date': image_date,
                  'image_name': image_name,
                  }
    return image_info


def get_image_info(token, url, folder_name):
    params = {
        'api_key': token,
    }
    response = requests.get(url, params)
    for image in response.json()[:2]:
        image_info = parse_image_info(image)
        download_epic_image(token, image_info, folder_name)


def download_spacex_images(links, images_path):
    load_dotenv()
    SPACEX_IMAGES_AMOUNT = int(os.environ.get('SPACEX_IMAGES_AMOUNT', '2'))
    Path(images_path).mkdir(parents=True, exist_ok=True)
    for num, link in enumerate(links[:SPACEX_IMAGES_AMOUNT]):
        response = requests.get(link)
        response.raise_for_status()
        image_path = f'{images_path}/spacex{str(num)}.jpg'
        with open(image_path, 'wb') as file:
            file.write(response.content)


def fetch_spacex_last_launch():
    response = requests.get('https://api.spacexdata.com/v3/launches/past')
    response.raise_for_status()
    images_list = [link for flight in response.json()
                   for link in flight['links']['flickr_images']]
    return images_list


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
    o = urlparse(url)
    filename, file_extension = os.path.splitext(o.path)
    return file_extension


def main():
    load_dotenv()
    AUTH_TOKEN = os.environ['AUTH_TOKEN']
    NASA_IMAGES_AMOUNT = int(os.environ.get('NASA_IMAGES_AMOUNT', '3'))
    nasa_url = 'https://api.nasa.gov/EPIC/api/natural/images'
    photos_path = 'space_photos'
    try:
        nasa_images = get_apod_images(AUTH_TOKEN, NASA_IMAGES_AMOUNT)
        save_nasa_apod(nasa_images, photos_path)
        spacex_last_launch_photos = fetch_spacex_last_launch()
        download_spacex_images(spacex_last_launch_photos, photos_path)
        get_image_info(AUTH_TOKEN, nasa_url, photos_path)
        send_images(photos_path)
        print('Фотографии отправлены в канал')
    except requests.exceptions.HTTPError:
        print('Проверьте введенную вами ссылку')


if __name__ == '__main__':
    main()
