import asyncio
import itertools
import logging
import os
import time
from io import BytesIO

import cv2
import httpx
import requests

logging.getLogger('asyncio').setLevel(100)

header = {
    'X-Auth-User': os.environ.get('X-Auth-User'),
    'X-Auth-Key': os.environ.get('X-Auth-Key'),
}


class S3Service:
    last_time_changed = time.monotonic()
    __x_storage_token = None

    @classmethod
    def cache_check(cls):
        if cls.__x_storage_token is None:
            return False

        if time.monotonic() - cls.last_time_changed > 60 * 5:
            return False
        return True

    @classmethod
    def get_token(cls):
        if not cls.cache_check():
            url = f"https://api.selcdn.ru/auth/v1.0"
            print('updated tokens')

            payload = {}
            response = requests.request("GET", url, headers=header, data=payload)
            try:
                cls.__x_storage_token = response.headers['x-storage-token']
                cls.last_time_changed = time.monotonic()
                return cls.__x_storage_token
            except Exception as e:
                print(e)
                return None
        else:
            return cls.__x_storage_token


class UrlToS3:

    @classmethod
    def get_token(cls):
        url = f"https://api.selcdn.ru/auth/v1.0"

        payload = {}
        response = requests.request("GET", url, headers=header, data=payload)
        try:
            return response.headers['x-storage-token']
        except Exception as e:
            print(e)
            return None

    @classmethod
    async def video_process(cls, url: str):
        try:
            cap = cv2.VideoCapture(url)
            i = 0
            cnt = None
            for _ in range(100):
                ret, frame = cap.read()
                if ret is False:
                    break

                i += 1
                # break
                if i > 5:
                    # print(type(frame.tobytes()))
                    success, encoded_image = cv2.imencode('.png', frame)
                    content2 = encoded_image.tobytes()
                    cnt = content2

                    break

            cap.release()
            return cnt
        except Exception as ee:
            print(ee)
            pass

    # photo:dict = {'photo_url':photo_s3}
    @classmethod
    async def get_data_from_link(cls, client, photo_url: str, photo_s3: str, headers):
        try:
            if not photo_url.__contains__('.mp4'):
                photo_s3 = f'{photo_s3}.jpg'
                r = await client.get(photo_url, timeout=60)
                if b'URL signature expired' in r.content or b'URL signature mismatch' in r.content:
                    print('URL signature expired', photo_s3)
                    return

                raw = BytesIO(r.content)
            else:
                try:
                    raw = await UrlToS3.video_process(photo_url)
                    raw = BytesIO(raw)
                except Exception as e:
                    # print(e)
                    return

            url = f"https://api.selcdn.ru/v1/SEL_103784/Фото Инстаграм/{photo_s3}"
            payload = {}
            files = [
                (f'{photo_s3}', (f'{photo_s3}', raw))
            ]

            await client.put(url, headers=headers, data=payload, files=files, timeout=60)

            # time_print('good photo', photo_s3, )

            raw.close()

            return True

        except Exception as e:
            print('--', e)
            return False

    @classmethod
    async def downloader(cls, photos: dict):
        headers = {
            'X-Auth-Token': f'{UrlToS3.get_token()}',
            'X-Delete-After': '9999999999999999999999999'
        }
        client = httpx.AsyncClient()
        tasks = []
        for photo_url, photo_s3 in photos.items():
            tasks.append(asyncio.ensure_future(UrlToS3.get_data_from_link(client, photo_url, photo_s3, headers)))
        tasks_result = await asyncio.gather(*tasks)
        await client.aclose()
        return tasks_result

    @classmethod
    async def async_push_to_kafka(cls, photos: dict):
        from flood.services.KafkaProducer import AsyncKafkaProducer
        await AsyncKafkaProducer.push(photos)

    @classmethod
    def push_to_kafka(cls, photos: dict):
        from flood.services.KafkaProducer import KafkaProducerPhotoVideo
        KafkaProducerPhotoVideo().push_dct(photos)

    @classmethod
    async def downloader_without_limit(cls, photos: dict):
        try:
            #
            from flood.services.KafkaProducer import KafkaProducerPhotoVideo

            KafkaProducerPhotoVideo().push_dct(photos)
        except Exception as e:
            print(e)

        return
        start = 0
        while True:
            photos_limit_100 = dict(itertools.islice(photos.items(), start, start + 100))
            start += 100
            print('photos', start, 'len', len(photos_limit_100))
            if len(photos_limit_100) == 0:
                print('photos done')
                break
            await UrlToS3.downloader(photos_limit_100)


if __name__ == '__main__':
    async def worker():
        urll = 'https://scontent-hel3-1.cdninstagram.com/v/t50.2886-16/241884081_1037417453692348_3498258656840166311_n.mp4?efg=eyJ2ZW5jb2RlX3RhZyI6InZ0c192b2RfdXJsZ2VuLjcyMC5mZWVkLmRlZmF1bHQiLCJxZV9ncm91cHMiOiJbXCJpZ193ZWJfZGVsaXZlcnlfdnRzX290ZlwiXSJ9&_nc_ht=scontent-hel3-1.cdninstagram.com&_nc_cat=104&_nc_ohc=m--J_91_ALcAX-yF46K&edm=ABfd0MgBAAAA&vs=18170533315194983_3400543960&_nc_vs=HBksFQAYJEdMSGJhZzY4cGNfU2hxOERBS2VyWkwyMlQ0d3dia1lMQUFBRhUAAsgBABUAGCRHT08tYlE3NE5STkdfeEFCQUJCN0pfSW9kU1IzYmtZTEFBQUYVAgLIAQAoABgAGwGIB3VzZV9vaWwBMBUAACbO4ejNxOLUPxUCKAJDMywXQC4AAAAAAAAYEmRhc2hfYmFzZWxpbmVfMV92MREAdeoHAA%3D%3D&_nc_rid=342ac45475&ccb=7-4&oe=61BADBED&oh=00_AT-o5ceMA8byt7skHfcsm6eI5M81wiLQ60d2IXcWzygWWw&_nc_sid=7bff83'
        urll2 = 'https://instagram.fhel3-1.fna.fbcdn.net/v/t51.2885-15/sh0.08/e35/s640x640/241876467_386170156470769_6557586971110428705_n.jpg?_nc_ht=instagram.fhel3-1.fna.fbcdn.net&_nc_cat=1&_nc_ohc=pAgucWd7Gs8AX9SxoLt&edm=ABfd0MgBAAAA&ccb=7-4&oh=00_AT-yuO7cTblm9moWSb4iaL0k-AZ46m6rNhwOW2EX8r3qQA&oe=61BAD893&_nc_sid=7bff83'
        dct = {
            urll: "test_test_url"
            ,
            urll2: 'url_url_test'
        }
        await UrlToS3.downloader(dct)


    asyncio.get_event_loop().run_until_complete(worker())
