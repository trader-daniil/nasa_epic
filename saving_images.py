import datetime
import os
import time
import imghdr
from os import listdir, path
from pathlib import Path
from urllib.parse import urlparse
import requests
import telegram
from dotenv import load_dotenv


def checking_if_image(file_path):
    return path.isfile(file_path) and imghdr.what(file_path)


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
        if checking_if_image(el_path):
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
    for image in response.json()[:2]:
        image_info = parsing_image_info(image)
        downloading_epic_image(token, image_info, folder_name)


def spacex_images_downloading(links, images_path):
    Path(images_path).mkdir(parents=True, exist_ok=True)
    for num, link in enumerate(links[:2]):
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
    return spacex_images_downloading(images_list, 'epics')


def nasa_apod(images_url, image_path):
    Path(image_path).mkdir(parents=True, exist_ok=True)
    for num, image_url in enumerate(images_url):
        response = requests.get(image_url)
        extension = getting_extension(image_url)
        image = f'{image_path}/apod{num}{extension}'
        with open(image, 'wb') as file:
            file.write(response.content)


def getting_apod_images(token, amount):
    url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'api_key': token,
        'count': amount,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    images = [flight['hdurl'] for flight in response.json() if flight]
    return nasa_apod(images, 'epics')


def getting_extension(url):
    o = urlparse(url)
    filename, file_extension = os.path.splitext(o.path)
    return file_extension


def main():
    load_dotenv()
    AUTH_TOKEN = os.environ['AUTH_TOKEN']
    NASA_URL = 'https://api.nasa.gov/EPIC/api/natural/images'
    try:
        getting_apod_images(AUTH_TOKEN, 5)
        fetch_spacex_last_launch()
        getting_image_info(AUTH_TOKEN, NASA_URL, 'epics')
        sending_images()
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
        SENDING_PERIOD = '5'
    main()
