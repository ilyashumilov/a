import json

import requests

from flood.modules.BaseFloodModel import BaseFloodModel
from flood.modules.ProfileDetail import clean_to_json
from flood.services.global_service import url_normalize
from main.models import Blogger
from parsing.AsyncParsingNew.utils import time_print
from parsing.NovemberParsing.url_to_s3 import UrlToS3
from rest.api.social.methods import util_methods

from flood.services.KafkaProducer import KafkaProducerPhotoVideo

KafkaProducerPhotoVideo()


def edit_blogger(blogger: Blogger, data: dict, avatars_dct: dict, cities_dct: dict):
    blogger.login = data.get('username')
    blogger.name = str(data.get('full_name')).replace('й', 'й')

    if blogger.social_id is None or len(str(blogger.social_id)) < 2:
        blogger.social_id = data.get('pk')

    blogger.avatar = f'{blogger.social_id}__{blogger.login}'

    hd_profile_pic_url_info: dict = data.get('hd_profile_pic_url_info')
    url: str = hd_profile_pic_url_info.get('url')
    url = url_normalize(url)

    avatars_dct[url] = blogger.avatar

    blogger.verification_type = 1 if data.get('is_verified') else None
    blogger.post_default_count = data.get("media_count")
    blogger.default_total = data.get('follower_count')
    blogger.following = data.get('following_count')
    blogger.bio = data.get('biography')
    blogger.category = data.get('category', None)
    blogger.external_link = data.get('external_url')
    blogger.status_id = 2 if data.get('is_private') else 1
    # blogger.engagement_rate = blogger.create_er()

    city_id = int(data.get('city_id', 0))
    if city_id != 0:
        cities_dct[city_id] = data.get('city_name')
        blogger.address_id = city_id


class FilteringBloggersDetail(BaseFloodModel):

    @classmethod
    async def limited_bloggers(cls, dct):
        bloggers = Blogger.objects.filter(login__in=list(dct.keys()), social_network_type_id=3)
        print('blogger len', len(bloggers))

        avatars_dct = {}
        cities_dct = {}

        for blogger in bloggers:
            value = dct[blogger.login]
            blogger: Blogger

            data: dict = value

            edit_blogger(blogger, data, avatars_dct, cities_dct)

            try:
                del dct[blogger.login]
            except:
                pass

        bloggers_new = []

        for login, value in dct.items():
            data: dict = value
            blogger = Blogger(login=data.get('username'), social_network_type_id=3)
            edit_blogger(blogger, data, avatars_dct, cities_dct)
            bloggers_new.append(blogger)

        await UrlToS3.downloader(avatars_dct)

        FilteringBloggersDetail.cities_creator(cities_dct)
        print('to upd', len(bloggers), 'to create', len(bloggers_new))
        Blogger.objects.bulk_update(bloggers, fields=['login', 'name', 'avatar', 'verification_type',
                                                      'post_default_count', 'default_total', 'following', 'bio',
                                                      'category', 'external_link', 'social_id', 'status_id',
                                                      'engagement_rate', 'address_id'
                                                      ], batch_size=1_000)

        # Blogger.objects.bulk_create(bloggers_new, ignore_conflicts=True, batch_size=5_000)
        print('all done')

    @classmethod
    async def from_file(cls, response: requests.Response, extra_data=None):
        response.encoding = 'utf-8'

        dct = {}

        counter = 0
        for i in response.iter_lines(chunk_size=10_000, decode_unicode=True):
            try:
                try:
                    social_id, login__, language, json_str_data = i.split(':', maxsplit=3)
                    if len(language) > 3:
                        raise
                except:
                    json_str_data = clean_to_json(i)

                data: dict = json.loads(json_str_data)['user']
            except Exception as e:
                print(e)
                continue

            blogger_login = data.get('username')
            dct[blogger_login] = data

            counter += 1

            if counter > 0 and counter % 500 == 0:
                time_print('limited subs', counter, 'count')
                await cls.limited_bloggers(dct.copy())
                dct.clear()

        time_print('limited subs', counter, 'end')
        await cls.limited_bloggers(dct.copy())
        dct.clear()
