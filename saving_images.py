import argparse
import datetime
import os
from pathlib import Path

import requests
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
    for image in response.json():
        image_info = parsing_image_info(image)
        downloading_epic_image(token, image_info, folder_name)


def main():
    load_dotenv()
    auth_token = os.environ['AUTH_TOKEN']
    parser = argparse.ArgumentParser(
        description='Программа скачивает изображения',
    )
    parser.add_argument('url', help='ссылка на изображения')
    args = parser.parse_args()
    try:
        getting_image_info(auth_token, args.url, 'epics')
        print('Фотографии загружены в папку')
    except requests.exceptions.HTTPError:
        print('Проверьте введенную вами ссылку')


if __name__ == '__main__':
    main()
