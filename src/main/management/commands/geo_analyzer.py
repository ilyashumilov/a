import time

import requests
from django.conf import settings
from django.core.management import BaseCommand
import asyncio

# geo_analyzer
from main.models import Address
from parsing.AsyncParsingNew.utils import time_print


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


async def get_city_country(address: str):
    url = f'{settings.GEO_IP}/api/geo'
    body = {
        "address": address
    }
    resp = requests.post(url, json=body)
    data = resp.json()
    return data['city'], data['country']


async def worker():
    while True:
        index = 0

        addresses = Address.objects.filter(auto_checked=False)[:10_000]
        size = addresses.count()

        for address in addresses:
            city, country = await get_city_country(address.city_name)
            address.native_city = city
            address.native_country = country
            address.auto_checked = True

            address.save(update_fields=['native_city', 'native_country', 'auto_checked'])

            index += 1
            time_print('index', index, 'size', size, 'point', address.city_name, '|| city', city, '|| country', country)

        time.sleep(60)
