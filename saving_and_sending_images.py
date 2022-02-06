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


def send_images_to_tgchat(images_path, bot_token, chat_id, sending_period):
    bot = telegram.Bot(token=bot_token)
    images = listdir(images_path)
    for image in images:
        full_image_path = path.join(
            images_path,
            image,
        )
        if is_image_appropriate(full_image_path):
            with open(full_image_path, 'rb') as image:
                bot.send_photo(
                    chat_id=chat_id,
                    photo=image,
                )
            time.sleep(int(sending_period))


def parse_image_info(image_date, image_name):
    image_date_format = '%Y-%m-%d %H:%M:%S'
    fetched_date = datetime.datetime.strptime(
        image_date,
        image_date_format,
    )
    image_date = fetched_date.strftime("%Y/%m/%d")
    image_info = {
        'image_date': image_date,
        'image_name': image_name,
    }
    return image_info


def get_epic_images_urls(token, number_of_image):
    nasa_url = 'https://api.nasa.gov/EPIC/api/natural/images'
    params = {
        'api_key': token,
    }
    response = requests.get(nasa_url, params)
    images_urls = []
    for image in response.json()[:number_of_image]:
        image_info = parse_image_info(
            image['date'],
            image['image'],
        )
        image_name = image_info['image_name']
        image_date = image_info['image_date']
        image_url = ('https://api.nasa.gov/EPIC/archive/natural/'
                     f'{image_date}/png/{image_name}.png')
        images_urls.append(image_url)
    return images_urls


def fetch_spacex_last_launch_links(images_amount):
    response = requests.get('https://api.spacexdata.com/v3/launches/past')
    response.raise_for_status()
    images_links = [link for flight in response.json()
                    for link in flight['links']['flickr_images']]
    return images_links[:images_amount]


def get_apod_images_urls(token, amount):
    url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'api_key': token,
        'count': amount,
    }
    response = requests.get(
        url,
        params=params,
    )
    response.raise_for_status()
    images_urls = [flight['hdurl'] for flight in response.json() if flight]
    return images_urls


def get_extension(url):
    image_url = urlparse(url)
    filename, file_extension = os.path.splitext(image_url.path)
    return file_extension


def downloading_image(image_url, image_path, image_name, token):
    extension = get_extension(image_url)
    full_image_path = f'{image_path}/image{image_name}{extension}'
    if token:
        params = {
            'api_key': token,
        }
        response = requests.get(
            image_url,
            params=params,
        )
    else:
        response = requests.get(image_url)
    with open(full_image_path, 'wb') as file:
        file.write(response.content)


def main():
    photos_path = os.environ.get(
        'IMAGES_PATH',
        'space_photos',
    )
    Path(photos_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    load_dotenv()
    nasa_token = os.environ['NASA_TOKEN']
    apod_images_amount = int(os.environ.get(
        'APOD_IMAGES_AMOUNT',
        '3',
    ))
    try:
        images_urls = []
        spacex_images_amount = int(os.environ.get(
            'SPACEX_IMAGES_AMOUNT',
            '2',
        ))
        images_urls += fetch_spacex_last_launch_links(spacex_images_amount)
        images_urls += get_apod_images_urls(
            nasa_token,
            apod_images_amount,
        )
        epic_images_amount = int(os.environ.get(
            'EPIC_IMAGES_AMOUNT',
            '3',
        ))
        images_urls += get_epic_images_urls(
            token=nasa_token,
            number_of_image=epic_images_amount
            )
        for url_num, url in enumerate(images_urls):
            token = None
            if 'nasa' in url:
                token = nasa_token
            downloading_image(
                image_url=url,
                image_path=photos_path,
                image_name=url_num,
                token=token
            )
        tg_bot_token = os.environ['TELEGRAM_BOT_TOKEN']
        tg_chat_id = os.environ['TELEGRAM_CHAT_ID']
        sending_period = os.environ.get(
            'SENDING_PERIOD',
            '86400',
        )
        send_images_to_tgchat(
            photos_path,
            tg_bot_token,
            tg_chat_id,
            sending_period,
        )
        print('Фотографии отправлены в канал')
    except requests.exceptions.HTTPError:
        print('Проверьте введенную вами ссылку')


if __name__ == '__main__':
    main()
