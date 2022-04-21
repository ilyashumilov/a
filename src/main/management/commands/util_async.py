import json
import time

import requests
from django.conf import settings
from django.core.management import BaseCommand
import asyncio

# util_async
from api.services import methods
from brand_parser.models import Brand
from intercalation.modules.FilteringSubscribersFlood import FilteringSubscribersFlood
from intercalation.modules.SubscribersFlood import SubscribersFlood
from main.management.commands.util import check_word
from main.models import Blogger, Post, Address
from parsing.NovemberParsing.url_to_s3 import UrlToS3
from parsing.management.commands.translator import Translate


def clean_to_json(line: str):
    try:
        if line[0] != '{':
            index = line.find(':{')
            return line[index + 1:]
    except:
        pass
    return line


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker(loop))


async def worker(loop):
    # translater = Translate()
    # brands = Brand.objects.filter(original_name=None)
    # for brand in brands:
    #     d = await translater.translate([brand.name], 'en')
    #     brand.original_name = d[0]
    # Brand.objects.bulk_update(brands, fields=['original_name'])
    #
    # return
    # response = requests.get('https://instaparser.ru/api.php?key=4Cb79evO8G16lJ30&tid=3752840&last=0&json=0')
    #
    # lat_long_dct={}
    # for line_i in response.iter_lines(chunk_size=10_000, decode_unicode=True):
    #     json_str_data = clean_to_json(line_i)
    #     data:dict = json.loads(json_str_data)['user']
    #     city_id=data.get('city_id')
    #     lat_long_dct[city_id] = f"{data.get('latitude')};{data.get('longitude')}"
    # addresses = Address.objects.filter(city_id__in=list(lat_long_dct))
    # for i in addresses:
    #     i.latitude_longitude = lat_long_dct[i.city_id]
    # Address.objects.bulk_update(addresses,fields=['latitude_longitude'],batch_size=5_090)
    #
    #
    #
    # print(len(lat_long_dct))
    #
    #
    #
    #
    #
    #
    #
    # return
    addresses = Address.objects.all()
    tr = Translate()
    for i in addresses:
        i: Address
        try:
            flag = False
            if check_word(i.native_city):
                data = await tr.translate([i.native_city], 'en')
                data = data[0]
                i.original_city = data
                flag = True
            if check_word(i.native_country):
                data = await tr.translate([i.native_country], 'en')
                data = data[0]
                i.original_country = data
                flag = True
            if flag:
                i.save(update_fields=['native_country', 'native_city'])
                print(i.native_city, '-->', i.original_city)
                print(i.original_country, '-->', i.original_country)

        except Exception as e:
            print(e)

    # for i in addresses:
    #     i: Address
    #     try:
    #         flag=False
    #         if not check_word(i.native_city):
    #             data = await tr.translate([i.native_city], 'ru')
    #             data = data[0]
    #             i.native_city = data
    #             flag=True
    #         if not check_word(i.native_country):
    #             data = await tr.translate([i.native_country], 'ru')
    #             data = data[0]
    #             i.native_country = data
    #             flag=True
    #         if flag:
    #             i.save(update_fields=['native_country', 'native_city'])
    #             print(i.native_country,i.native_city)
    #     except Exception as e:
    #         pass
