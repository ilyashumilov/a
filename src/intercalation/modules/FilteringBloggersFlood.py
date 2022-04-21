import json
import typing

import requests

from intercalation.base_modules.BaseFloodModel import BaseFloodModel
from intercalation.services import bloggers_service
from main.models import Blogger
from parsing.NovemberParsing.url_to_s3 import UrlToS3


class FilteringBloggersFlood(BaseFloodModel):
    @classmethod
    async def from_file(cls, response: requests.Response, extra_data=None):
        response.encoding = 'utf-8'
        cities_dct = {}
        lat_long_dct = {}
        counter = 0
        bloggers_dct = {}
        avatars = {}
        languages_dct = {}
        obj_to_lang = {}

        categories_dct = {}
        obj_to_category = {}

        is_advertiser = (extra_data is not None and 'is_advertiser' in extra_data)

        for line_i in response.iter_lines(chunk_size=10_000, decode_unicode=True):
            try:
                json_str_data = cls.json_reader(line_i, languages_dct, obj_to_lang)

                data = json.loads(json_str_data)['user']
                social_id = str(data.get('pk'))

                blogger = cls.create_blogger(data, social_id, cities_dct, lat_long_dct)
                avatar = f'{blogger.social_id}__{blogger.login}'
                avatars[avatar] = blogger.avatar
                blogger.avatar = avatar

                if is_advertiser:
                    blogger.is_advertiser = is_advertiser

                cls.extract_category(social_id, data, categories_dct, obj_to_category)
                bloggers_dct[social_id] = blogger
                counter += 1

                if counter > 0 and counter % 10_000 == 0:
                    cls.process(bloggers_dct, avatars, languages_dct, obj_to_lang,
                                categories_dct, obj_to_category, cities_dct, lat_long_dct)

            except Exception as e:
                print(e)
                continue
        if len(bloggers_dct) > 0:
            try:
                cls.process(bloggers_dct, avatars, languages_dct, obj_to_lang,
                            categories_dct, obj_to_category, cities_dct, lat_long_dct)
            except:
                pass

    @classmethod
    def create_blogger(cls, data: dict, social_id: str, cities_dct: dict, lat_long_dct: dict) -> Blogger:
        dct = {}
        dct['login'] = data['username']
        dct['social_id'] = social_id
        dct['name'] = data['full_name']
        dct['social_network_type_id'] = 3

        dct['default_total'] = data['follower_count']
        dct['following'] = data['following_count']
        dct['post_default_count'] = data['media_count']

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

        return Blogger(**dct)

    @classmethod
    def process(cls, bloggers_dct, avatars, languages_dct, obj_to_lang,
                categories_dct, obj_to_category, cities_dct, lat_long_dct):

        cls.language_category(languages_dct, categories_dct)

        for k, blogger in bloggers_dct.items():
            blogger: Blogger
            try:
                blogger.language_id = languages_dct[obj_to_lang[k]]
            except:
                pass
            try:
                blogger.category_id = categories_dct[obj_to_category[k]]
            except:
                pass
        cls.cities_creator(cities_dct.copy(), lat_long_dct.copy())

        cities_dct.clear()
        languages_dct.clear()
        obj_to_lang.clear()
        categories_dct.clear()
        obj_to_category.clear()
        lat_long_dct.clear()

        cls.update_bloggers(bloggers_dct)

        try:
            UrlToS3.push_to_kafka(avatars.copy())
        except Exception as e:
            print(e)

        avatars.clear()

    @classmethod
    def update_bloggers(cls, bloggers_dct: dict):
        exists_bloggers = Blogger.objects.filter(social_network_type_id=3, social_id__in=list(bloggers_dct))
        for exist_blogger in exists_bloggers:
            new_blogger: Blogger = bloggers_dct[exist_blogger.social_id]
            bloggers_service.update_fields(exist_blogger, new_blogger)

            try:
                del bloggers_dct[exist_blogger.social_id]
            except:
                pass

        new_bloggers = list(bloggers_dct.values())
        for new_blogger in new_bloggers:
            if 'lk_potok' not in new_blogger.file_from_info:
                new_blogger.file_from_info.append('lk_potok')

        Blogger.objects.bulk_update(exists_bloggers, fields=bloggers_service.get_fields(), batch_size=5_000)
        Blogger.objects.bulk_create(new_bloggers, ignore_conflicts=True)

        bloggers_dct.clear()
