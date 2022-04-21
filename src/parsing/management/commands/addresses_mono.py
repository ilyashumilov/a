from django.core.management import BaseCommand
import asyncio

# addresses_mono
from main.models import Address


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="hehe")
cities_keys = ("city", "state",'region', "province", "county", "town")


def get_city_country(search: str):
    try:
        location = geolocator.geocode(search, language='ru')

        location = geolocator.reverse(f'{location.latitude},{location.longitude}', language='ru')
        # print(location.address)
        address = location.raw.get('address')
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

def check_word(word: str):
    alf = list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    for i in word:
        if i in alf:
            return True
    return False

def get_city_country_by_lat_lng(lat_lng: str):
    try:
        location = geolocator.reverse(f'{lat_lng.replace(";", ",")}', language='ru')
        address = location.raw.get('address')
        city = None
        for key in cities_keys:
            city = address.get(key, None)
            if city is not None and check_word(city):
                break
        if city is None:
            for key in cities_keys:
                city = address.get(key, None)
                if city is not None:
                    break

        country = address.get('country')
        print(lat_lng, "||", city, "||", country)
        return city, country
    except:
        return None, None


async def worker():
    while True:
        addresses = Address.objects.filter(auto_checked=False)[:500]
        for address in addresses:
            flag = False
            if ';' in str(address.latitude_longitude):
                city, country = get_city_country_by_lat_lng(address.latitude_longitude)
                if city is not None:
                    flag = True

            if not flag:
                city, country = get_city_country(address.city_name)

            address.native_city = city
            address.native_country = country
            address.auto_checked = True
            address.save(update_fields=['native_city', 'native_country', 'auto_checked'])
