import typing

import requests

from main.models import Address, Language, Category


class BaseFloodModel(object):
    @classmethod
    async def from_file(cls, response: requests.Response, blogger_login: typing.Optional[str]):
        pass

    @classmethod
    def cities_creator(cls, cities_dct: dict, lat_long_dct: dict):
        addresses = Address.objects.filter(city_id__in=list(cities_dct.keys())).only('city_id')
        arr = []
        for address in addresses:
            del cities_dct[address.city_id]
            lat_long = lat_long_dct[address.city_id]
            address.latitude_longitude = lat_long
            arr.append(address)
        Address.objects.bulk_update(arr, fields=['latitude_longitude'])

        arr = []
        for city_id, address in cities_dct.items():
            lat_long = lat_long_dct[city_id]
            arr.append(Address(city_id=city_id, city_name=address, latitude_longitude=lat_long))
        Address.objects.bulk_create(arr, batch_size=1_000, ignore_conflicts=True)

    @classmethod
    def clean_to_json(cls, line: str):
        try:
            if line[0] != '{':
                index = line.find(':{')
                return line[index + 1:]
        except:
            pass
        return line

    @classmethod
    def extract_city(cls, data: dict, cities_dct: dict, lat_long_dct: dict):
        try:
            city_id = int(data.get('city_id', 0))
            if city_id != 0:
                cities_dct[city_id] = data.get('city_name')
                lat_long_dct[city_id] = f"{data.get('latitude')};{data.get('longitude')}"

                return city_id
            else:
                return None
        except:
            return None

    @classmethod
    def extract_category(cls, social_id: str, data: dict, categories_dct: dict, obj_to_category: dict):
        category = data.get('category', None)
        if category is None:
            return
        categories_dct[category] = None
        obj_to_category[social_id] = category

    @classmethod
    def language_category(cls, languages_dct: dict, categories_dct: dict):
        languages = list(languages_dct)
        exists_langs = Language.objects.filter(name__in=languages).values_list('name', flat=True)
        languages_not_exists = set(languages) - set(list(exists_langs))
        languages_new = []
        for i in languages_not_exists:
            languages_new.append(Language(name=i))
        Language.objects.bulk_create(languages_new, ignore_conflicts=True)
        languages = Language.objects.filter(name__in=languages).only('id', 'name')
        for language in languages:
            languages_dct[language.name] = language.id

        categories = list(categories_dct)
        exists_catgs = Category.objects.filter(name__in=categories).values_list('name', flat=True)
        categories_not_exists = set(categories) - set(list(exists_catgs))
        categories_new = []
        for i in categories_not_exists:
            categories_new.append(Category(name=i))
        Category.objects.bulk_create(categories_new, ignore_conflicts=True)
        categories = Category.objects.filter(name__in=categories).only('id', 'name')
        for category in categories:
            categories_dct[category.name] = category.id

    @classmethod
    def change(cls, first, second, field: str):
        setattr(first, field, getattr(second, field, None))

    @classmethod
    def json_reader(cls, line_i, languages_dct, obj_to_lang):
        try:
            social_id__, login__, language, json_str_data = line_i.split(':', maxsplit=3)
            if '{' in social_id__ or '{' in login__ or '{' in language:
                raise

            language: str = language.strip().replace('0', '')
            # todo language
            if len(language) > 0:
                languages_dct[language] = None
                obj_to_lang[social_id__] = language

        except:
            json_str_data = cls.clean_to_json(line_i)

        return json_str_data
