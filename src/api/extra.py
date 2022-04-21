import os
import time

import requests
from django.http import HttpRequest

from core import settings
from parsing.NovemberParsing.url_to_s3 import UrlToS3

s3_header = {
    'X-Auth-User': os.environ.get('X-Auth-User'),
    'X-Auth-Key': os.environ.get('X-Auth-Key'),
}


def get_headers():
    headers = {
        'X-Auth-Token': f'{UrlToS3.get_token()}',
        'X-Delete-After': '9999999999999999999999999'
    }
    return headers


def reload_headers(headers: dict):
    headers['X-Auth-Token'] = f'{UrlToS3.get_token()}'





def rounder(er: float):
    return round(er, 4)


# template_image
def photo_download(content):
    a = content.rfind(b'Content-Type: image/jpeg') + len(b'Content-Type: image/jpeg\r\n\r\n')
    data = content[a:]
    return data


def photo_download_from_s3(photo_s3: str):
    headers = get_headers()
    headers_time_alive = time.monotonic()

    if (time.monotonic() - headers_time_alive) > 60 * 30:
        reload_headers(headers)

    url = f'https://api.selcdn.ru/v1/SEL_103784/Фото Инстаграм/{photo_s3}.jpg'
    r = requests.get(url, headers=headers, stream=True)
    content = r.content
    if b'The resource could not be found.' not in content:
        return photo_download(r.content)
    else:
        return photo_download_from_s3("1UtNFsVHYexDxeRsrxUYvLWDGO7JrV6hM")


def create_photo_link(photo: str, request: HttpRequest = None):
    if photo is None or len(str(photo)) < 2:
        return None
    host = settings.BASE_URL if request is None else request.get_host()
    return f'http://{host}/api/photo/{photo}/'
