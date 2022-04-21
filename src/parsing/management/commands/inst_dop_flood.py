import asyncio
import time

import requests
from django.conf import settings
from django.core.management import BaseCommand

# inst_dop_flood
from api.models import City, Country
from main.models import AccountParser, Blogger
from parsing.AsyncParsingNew.utils import time_print
from parsing.NovemberParsing.flood_subscribers_dop_module import FloodSubscriberDopModule
from tortoise_base import SubscriberAsync, db_init


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        loop = asyncio.get_event_loop()
        loop.create_task(worker())
        loop.run_forever()


def download(tid: int, parser: AccountParser):
    while True:
        try:
            url = f'{parser.base_url}api.php?key={parser.api_key}&mode=result&tid={tid}'
            response = requests.get(url.format(tid))
            response.encoding = 'utf-8'
            return response
        except Exception as e:
            print(e, 'sleep')


def get_county_city(country_city: str):
    # Ankara, Turkey
    # Comilla
    if country_city == '0' or country_city == "":
        return None, None
    elif len(country_city.split(',', maxsplit=1)) == 2:
        print(country_city, 'country_city two')
        city, country = country_city.split(',', maxsplit=1)
        city_id, _ = City.objects.get_or_create(name=city.strip())
        country_id, _ = Country.objects.get_or_create(name=country.strip())
        return city_id.id, country_id.id

    else:
        print(country_city, 'country_city one')
        city_id, _ = City.objects.get_or_create(name=country_city.strip())
        return city_id.id, None


async def worker():
    db = settings.DATABASES['default']
    await db_init(db)

    text = """justking31""".strip().split('\n')
    text = list(map(lambda x: f'{x.strip()}', text))

    text = set(text)
    fsm = FloodSubscriberDopModule()
    parser = AccountParser.objects.get(login='hypepotok3')
    url = f'{parser.base_url}api.php?key={parser.api_key}&mode=status&status=3'
    data = requests.get(url).json()
    dct = {}
    for i in data['tasks']:
        name = str(i['name']).replace('##','')
        if i['name'].startswith('##') and name in text:
            dct[name] = {
                'blogger_id': Blogger.objects.get(login=name).id,
                'tid': i['tid']
            }
            text.remove(name)
    print(len(dct), dct)
    time.sleep(3)


    for i, v in dct.items():
        try:
            response = download(v['tid'], parser)
            counter = 0
            arr = []
            for chunk in response.text.split('\n'):
                line: str = chunk.replace('\n', '').replace('\x00', '')
                social_id, login, country_city, language = line.split(':')
                city_id, country_id = get_county_city(country_city)
                if language == '0':
                    language = None
                arr.append(SubscriberAsync(social_id=social_id, login=login, city_id=city_id,
                                           country_id=country_id, language=language))

                if counter > 0 and counter % 10_000 == 0:
                    await fsm.prepare_flood(arr, v['blogger_id'])
                    time_print(counter, v)
                    arr.clear()

                counter += 1
            if len(arr) > 0:
                await fsm.prepare_flood(arr, v['blogger_id'])
                time_print(counter, v)
                arr.clear()
        except Exception as e:
            time_print(e, i, v)
