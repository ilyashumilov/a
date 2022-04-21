import json

import requests

from flood.modules.BaseFloodModel import BaseFloodModel
from flood.modules.ProfileDetail import clean_to_json
from flood.services.global_service import url_normalize
from main.models import Subscriber
from parsing.AsyncParsingNew.utils import time_print
from parsing.NovemberParsing.url_to_s3 import UrlToS3

from flood.services.KafkaProducer import KafkaProducerPhotoVideo
KafkaProducerPhotoVideo()
class FilteringAccountsDetail(BaseFloodModel):

    @classmethod
    async def from_file(cls, response: requests.Response, blogger_login=None):
        response.encoding = 'utf-8'

        dct = {}
        counter = 0
        for i in response.iter_lines(chunk_size=10_000, decode_unicode=True):
            try:
                try:
                    social_id, login__, language, json_str_data = i.split(':', maxsplit=3)
                    if len(language) > 3:
                        raise

                    language = language.strip().replace('0', '')
                    if len(language) == 0:
                        language = None

                except:
                    json_str_data = clean_to_json(i)
                    language = None

                data: dict = json.loads(json_str_data)['user']
            except Exception as e:
                print(e,i)
                continue


            data['language'] = language

            subscriber_social_id = str(data.get('pk'))
            dct[subscriber_social_id] = data

            counter += 1

            if counter > 0 and counter % 500 == 0:
                time_print('limited subs', counter, 'count')
                await cls.limited_subscribers(dct.copy())
                dct.clear()

        time_print('limited subs', counter, 'end')
        await cls.limited_subscribers(dct.copy())
        dct.clear()

    @classmethod
    async def limited_subscribers(cls, dct):
        subscribers = Subscriber.objects.filter(social_id__in=list(dct.keys()), social_type_id=3)

        avatars_dct = {}
        cities_dct = {}
        for subscriber in subscribers:
            value = dct[subscriber.social_id]
            subscriber: Subscriber

            data: dict = value

            subscriber.login = data.get('username')
            subscriber.name = str(data.get('full_name')).replace('й', 'й')

            subscriber.avatar = f'{subscriber.social_id}__{subscriber.login}'

            hd_profile_pic_url_info: dict = data.get('hd_profile_pic_url_info')
            url: str = hd_profile_pic_url_info.get('url')
            url = url_normalize(url)

            avatars_dct[url] = subscriber.avatar

            subscriber.verification_type_id = 1 if data.get('is_verified') else None
            subscriber.contents = data.get("media_count")
            subscriber.followers = data.get('follower_count')
            subscriber.following = data.get('following_count')
            subscriber.bio = data.get('biography')
            subscriber.is_business_account = data.get('is_business')
            subscriber.category = data.get('category', None)
            subscriber.language = data.get('language', None)

            city_id = int(data.get('city_id', 0))
            if city_id != 0:
                cities_dct[city_id] = data.get('city_name')
                subscriber.address_id = city_id

        FilteringAccountsDetail.cities_creator(cities_dct)
        await UrlToS3.downloader_without_limit(avatars_dct)
        time_print('lens to upd bulk update', len(subscribers))
        Subscriber.objects.bulk_update(subscribers, fields=['login', 'name', 'avatar', 'verification_type_id',
                                                              'contents', 'followers', 'following', 'bio',
                                                              'is_business_account', 'category',
                                                              'address_id', 'language'
                                                              ], batch_size=5_000)
