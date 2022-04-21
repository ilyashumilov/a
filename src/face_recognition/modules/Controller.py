import os
import time
from asyncio import AbstractEventLoop

import aiohttp
from django.conf import settings

from parsing.NovemberParsing.url_to_s3 import UrlToS3, S3Service


async def photo_download(content: bytes):
    a = content.rfind(b'Content-Type: image/jpeg') + len(b'Content-Type: image/jpeg\r\n\r\n')
    data = content[a:]
    bad_sequences = (b'URL signature expired', b'URL signature mismatch',
                     b'The resource could not be found.', b'Unauthorized')

    for i in bad_sequences:
        if i in content:
            return None
    return data


class Controller(object):
    def __init__(self, loop: AbstractEventLoop):
        self.current_time = time.monotonic()
        self.loop = loop

        self.__headers = {
            'Content-Type': 'image/jpeg',
        }

    async def get_photo(self, photo_s3: str):
        headers = {
            'X-Auth-Token': f'{S3Service.get_token()}',
            'X-Delete-After': '9999999999999999999999999'
        }
        url = f'https://api.selcdn.ru/v1/SEL_103784/Фото Инстаграм/{photo_s3}.jpg'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=60) as resp:
                return await photo_download(await resp.content.read())

    async def get_face_properties(self, content):
        url = f'http://{settings.FACE_URL}/v2/detect?age=on&gender=on'
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.__headers, data=content, timeout=20) as resp:
                return await resp.json()
