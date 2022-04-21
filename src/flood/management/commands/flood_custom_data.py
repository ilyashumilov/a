import os
import sys

import requests
from django.conf import settings
from django.core.management import BaseCommand
import asyncio

# flood_custom_data
from intercalation.modules.PostsFlood import PostsFlood
from intercalation.modules.FilteringBloggersFlood import FilteringBloggersFlood
from intercalation.modules.PostsFloodV2 import PostsFloodV2
from parsing.AsyncParsingNew.utils import time_print


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


def read_file(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read().strip().split('\n')
    return data


class TestResponse:
    def __init__(self, text):
        self.text = text


async def worker():
    base_path = os.path.abspath(os.path.join(settings.BASE_DIR, '..'))
    print(base_path)

    # data = read_file(r'C:\Users\Marat\Documents\GitHub\python_github\potok\HypeProject\Фильтрация_аккаунтов_-_06.03_22-03.txt')
    # TestResponse(data)
    # response = requests.get('https://instaparser.ru/api.php?key=C2Sa98Aph090EZ4b&tid=3324315&last=0&json=0')
    # counter = 0
    # await PostsDetail.from_file(response, 'dkorobovv')
    # with open(r'C:\Users\Marat\Documents\GitHub\python_github\potok\HypeProject\Фильтрация_аккаунтов_-_06.03_22-10.txt', 'r',
    #           encoding='utf-8') as f:
    #     line = f.read().strip()
    #
    # response = TestResponse(line)
    response = requests.get('https://instaparser.ru/api.php?key=9vVV83uE6x7976K8&tid=3978940&last=0&json=0')
    await FilteringBloggersFlood.from_file(response,None)
    return
    for line in data:
        try:
            response = TestResponse(line)
            time_print(counter, 'of', size)
            await PostsDetail.from_file(response, 'dkorobovv')
            time_print('finish')
            counter += 1

        except Exception as e:
            print(e)
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
