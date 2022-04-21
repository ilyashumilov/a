from django.core.management import BaseCommand
import asyncio

# ultimater
from parsing.AsyncParsingNew.utils import time_print


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


from geopy.geocoders import Nominatim

from main.models import Address
from parsing.management.commands.translator import Translate

geolocator = Nominatim(user_agent="hehe")


def get_city_country(search: str):
    try:
        location = geolocator.geocode(search, language='ru')

        location = geolocator.reverse(f'{location.latitude},{location.longitude}', language='ru')
        # print(location.address)
        address = location.raw.get('address')
        cities_keys = ("state", "town", "city")
        city = None
        for key in cities_keys:
            city = address.get(key, None)
            if city is not None:
                break
        if city is None:
            city = search
        country = address.get('country')
        print(search, "||", city, "||", country)
        return city, country
    except Exception as e:
        print(search, '|-|', e)
        return None, None


async def worker():
    with open(r'C:\Users\Marat\Documents\GitHub\python_github\potok\HypeProject\src\ids.csv', 'r') as f:
        data = list(f.read().strip().split('\n'))

    data = list(map(int, data))
    tr = Translate()
    addresses = Address.objects.filter(city_id__in=data)
    size = len(addresses)
    counter = 0
    for address in addresses:
        t = address.city_name
        city_name_natives = await tr.translate([t], 'ru')
        city_name_native: str = city_name_natives[0]
        native_city, native_country = get_city_country(city_name_native)
        try:
            if native_city is None and native_country is None:
                city_name_native = city_name_native[:city_name_native.rfind(',')]
                native_city, native_country = get_city_country(city_name_native)
        except:
            pass
        print(address.city_name,' ||| ', city_name_native, ' | ', native_city, native_country)

        address.native_city = native_city
        address.native_country = native_country
        counter += 1
        address.save(update_fields=['native_city', 'native_country'])

        time_print('counter', counter, 'size', size)
