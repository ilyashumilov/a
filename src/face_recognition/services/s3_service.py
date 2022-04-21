import os
import time

import requests

from parsing.NovemberParsing.url_to_s3 import UrlToS3

s3_header = {
    'X-Auth-User': os.environ.get('X-Auth-User'),
    'X-Auth-Key': os.environ.get('X-Auth-Key'),
}
headers = {
    'X-Auth-Token': f'{UrlToS3.get_token()}',
    'X-Delete-After': '9999999999999999999999999'
}

headers_time_alive = time.monotonic()


def photo_download(content):
    a = content.rfind(b'Content-Type: image/jpeg') + len(b'Content-Type: image/jpeg\r\n\r\n')
    data = content[a:]
    return data


def reload_headers(__headers: dict):
    __headers['X-Auth-Token'] = f'{UrlToS3.get_token()}'


def get_photo_raw(photo_s3: str):
    if (time.monotonic() - headers_time_alive) > 60 * 30:
        reload_headers(headers)

    url = f'https://api.selcdn.ru/v1/SEL_103784/Фото Инстаграм/{photo_s3}.jpg'
    r = requests.get(url, headers=headers, stream=True)
    photo = photo_download(r.content)
    return photo
