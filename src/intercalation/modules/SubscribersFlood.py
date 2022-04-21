import json
import typing

import requests

from intercalation.base_modules.BaseFloodModel import BaseFloodModel
from intercalation.services import subscribers_service
from main.models import Blogger, Subscriber
from parsing.AsyncParsingNew.utils import time_print
from parsing.NovemberParsing.url_to_s3 import UrlToS3


class SubscribersFlood(BaseFloodModel):
    @classmethod
    async def from_file(cls, response: requests.Response, blogger_login: typing.Optional[str]):
        response.encoding = 'utf-8'
        cities_dct = {}
        lat_long_dct = {}
        blg = Blogger.objects.get_default(login=blogger_login)
        counter = 0
        subscribers_dct = {}
        avatars = {}
        languages_dct = {}
        obj_to_lang = {}

        categories_dct = {}
        obj_to_category = {}

        for line_i in response.iter_lines(chunk_size=10_000, decode_unicode=True):
            try:
                json_str_data = cls.json_reader(line_i, languages_dct, obj_to_lang)

                data = json.loads(json_str_data)['user']
                social_id = str(data.get('pk'))

                subscriber = cls.create_subscriber(data, social_id, cities_dct, blg, lat_long_dct)
                avatar = f'{subscriber.social_id}__{subscriber.login}'
                avatars[avatar] = subscriber.avatar
                subscriber.avatar = avatar
                cls.extract_category(social_id, data, categories_dct, obj_to_category)
                subscribers_dct[social_id] = subscriber
                counter += 1

                if counter > 0 and counter % 10_000 == 0:
                    cls.process(subscribers_dct, avatars, languages_dct, obj_to_lang,
                                categories_dct, obj_to_category, cities_dct, lat_long_dct)

            except Exception as e:
                print(e)
                continue
        if len(subscribers_dct) > 0:
            try:
                cls.process(subscribers_dct, avatars, languages_dct, obj_to_lang,
                            categories_dct, obj_to_category, cities_dct, lat_long_dct)
            except:
                pass

    @classmethod
    def create_subscriber(cls, data: dict, social_id: str, cities_dct: dict, blg: Blogger, lat_long_dct) -> Subscriber:
        dct = {}
        dct['login'] = data['username']
        dct['social_id'] = social_id
        dct['name'] = data['full_name']
        dct['social_network_type_id'] = 3

        dct['bloggers'] = [blg.id]

        dct['followers'] = data['follower_count']
        dct['following'] = data['following_count']
        dct['contents'] = data['media_count']

        dct['status_id'] = 2 if data['is_private'] else 1
        dct['verification_type_id'] = 1 if data['is_verified'] else None
        dct['avatar'] = str(data['profile_pic_url']).replace(r'\u0026', '&')
        dct['bio'] = data['biography']

        # category

        dct['external_link'] = data.get('external_url', None)

        dct['address_id'] = cls.extract_city(data, cities_dct, lat_long_dct)

        # language

        dct['is_business_account'] = data['is_business']
        dct['email'] = data.get('public_email', None)
        dct['phone_number'] = data.get('contact_phone_number', None)

        return Subscriber(**dct)

    @classmethod
    def process(cls, subscribers_dct, avatars, languages_dct, obj_to_lang,
                categories_dct, obj_to_category, cities_dct, lat_long_dct):
        cls.language_category(languages_dct, categories_dct)
        for k, subscriber in subscribers_dct.items():
            subscriber: Subscriber
            try:
                subscriber.language_id = languages_dct[obj_to_lang[k]]
            except:
                pass
            try:
                subscriber.category_id = categories_dct[obj_to_category[k]]
            except:
                pass
        cls.cities_creator(cities_dct.copy(), lat_long_dct.copy())

        cities_dct.clear()
        languages_dct.clear()
        obj_to_lang.clear()
        categories_dct.clear()
        obj_to_category.clear()
        lat_long_dct.clear()

        cls.update_subscribers(subscribers_dct)

        try:
            UrlToS3.push_to_kafka(avatars.copy())
        except Exception as e:
            print(e)

        avatars.clear()

    @classmethod
    def update_subscribers(cls, subscribers_dct: dict):
        exists_subscribers = Subscriber.objects.filter(social_network_type_id=3, social_id__in=list(subscribers_dct))
        for exist_subscriber in exists_subscribers:
            new_subscriber: Subscriber = subscribers_dct[exist_subscriber.social_id]
            subscribers_service.update_fields(exist_subscriber, new_subscriber)

            if new_subscriber.bloggers[0] not in exist_subscriber.bloggers:
                exist_subscriber.bloggers.append(new_subscriber.bloggers[0])

            del subscribers_dct[exist_subscriber.social_id]

        Subscriber.objects.bulk_update(exists_subscribers, fields=subscribers_service.get_fields_detail(),
                                       batch_size=2500)

        cls.insert_subscribers(subscribers_dct)

    @classmethod
    def insert_subscribers(cls, subscribers_dct: dict):
        Subscriber.objects.bulk_create(list(subscribers_dct.values()), batch_size=10_000, ignore_conflicts=True)
        subscribers_dct.clear()
