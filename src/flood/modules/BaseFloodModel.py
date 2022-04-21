import requests

from main.models import Address


class BaseFloodModel(object):
    @classmethod
    async def from_file(cls, response: requests.Response, blogger_login: str):
        pass

    @classmethod
    def cities_creator(cls, cities_dct: dict):
        addresses = Address.objects.filter(city_id__in=list(cities_dct.keys())).only('city_id')
        for address in addresses:
            del cities_dct[address.city_id]
        arr = []
        for city_id, address in cities_dct.items():
            arr.append(Address(city_id=city_id, city_name=address))
        Address.objects.bulk_create(arr, batch_size=1_000, ignore_conflicts=True)
