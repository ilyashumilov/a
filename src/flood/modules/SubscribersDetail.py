import json
import time

import requests
import itertools

from django.db.models import QuerySet

from api.models import Country, City
from flood.modules.BaseFloodModel import BaseFloodModel
from main.models import Subscriber, Blogger, Address
from parsing.NovemberParsing.url_to_s3 import UrlToS3
from parsing.ParsingModules.ParsingModule import time_print

city_dct = {}
country_dct = {}
for i in City.objects.all().only('id', 'name'):
    city_dct[i.name.lower()] = i.id

for i in Country.objects.all().only('id', 'name'):
    country_dct[i.name.lower()] = i.id


def detect_city_country(city_country: str):
    if city_country == '0' or len(city_country) < 3:
        return None, None
    if ',' not in city_country:
        try:
            return city_dct[city_country.lower()], None
        except:
            city, created = City.objects.get_or_create(name=city_country)
            return city.id, None
    elif ',' in city_country:
        t = city_country.strip().split(',')
        city_name = t[0]
        country_name = t[-1]

        # city_name, country_name = city_country.strip().split(',')
        city_name = city_name.strip()
        country_name = country_name.strip()
        city, _ = City.objects.get_or_create(name=city_name)
        country, _ = Country.objects.get_or_create(name=country_name)
        return city.id, country.id
    else:
        return None, None


def change(first: Subscriber, second: Subscriber, field: str):
    setattr(first, field, getattr(second, field))


class SubscriberDetail(BaseFloodModel):


    @classmethod
    def from_json_data_to_dct_normal(cls, json_str_data: str, cities_dct: dict):
        t: dict = json.loads(json_str_data)['user']
        dct = {}
        dct['login'] = t['username']
        dct['followers'] = t['follower_count']
        dct['following'] = t['following_count']
        dct['contents'] = t['media_count']
        dct['name'] = t['full_name']
        dct['bio'] = t['biography']
        dct['avatar'] = str(t['profile_pic_url']).replace(r'\u0026', '&')
        dct['verification_type_id'] = 1 if t['is_verified'] else None
        dct['is_business_account'] = t['is_business']

        city_id = int(t.get('city_id', 0))
        if city_id != 0:
            cities_dct[city_id] = t.get('city_name')
            dct['address_id'] = city_id
        else:
            dct['address_id'] = None

        try:
            dct['category'] = t['category']
        except:
            dct['category'] = None
        return dct

    @classmethod
    async def process(cls, counter, blogger_login, avatars, dct, cities_dct: dict):
        start = 0
        time_print("counter", counter, 'avatars start', "login", blogger_login)
        while True:
            t_avatars = dict(itertools.islice(avatars.items(), start, start + 100))
            start += 100
            if len(t_avatars.keys()) == 0:
                break


            time_print('UrlToS3.downloader_without_limit')
            await UrlToS3.downloader_without_limit(t_avatars)

            time_print('avatars process', "login", blogger_login, 'offset', start)

        SubscriberDetail.cities_creator(cities_dct)
        not_exists: dict = SubscriberDetail.update_exists_subscribers(dct)
        time_print("login", blogger_login, 'exists done')
        SubscriberDetail.flood(not_exists)
        time_print("login", blogger_login, 'flood done')

        #             todo flood and update
        dct.clear()
        avatars.clear()

    @classmethod
    async def from_file(cls, response: requests.Response, blogger_login: str):
        response.encoding = 'utf-8'
        cities_dct = {}
        blg = Blogger.objects.get(login=blogger_login, social_network_type_id=3)
        counter = 0
        dct = {}
        avatars = {}
        for line_i in response.iter_lines(chunk_size=10_000, decode_unicode=True):
            # "9125392205:bahromjondavlatzoda:0:rus:{"user":::::"
            # 2315786905:bogat.99:Omsk, Russia:rus:

            # i: str
            try:
                social_id,login__, language, json_str_data = line_i.split(':', maxsplit=3)
                language: str = language.strip().replace('0', '')
                # city_id, country_id = detect_city_country(city_country)
                subscriber = Subscriber(social_id=social_id,
                                          social_type_id=3,
                                          city_id=None,
                                          country_id=None,
                                          language=language,
                                          bloggers=[blg.id],
                                          **SubscriberDetail.from_json_data_to_dct_normal(json_str_data, cities_dct)
                                          )
                avatars[subscriber.avatar] = f'{subscriber.social_id}__{subscriber.login}'
                subscriber.avatar = f'{subscriber.social_id}__{subscriber.login}'
                dct[subscriber.social_id] = subscriber

                counter += 1
            except Exception as e:
                time_print(blogger_login,e, 'error', line_i[:30])
            if counter > 0 and counter % 10_000 == 0:
                await SubscriberDetail.process(counter, blogger_login, avatars, dct, cities_dct)

        if len(avatars.keys()) > 0:
            await SubscriberDetail.process(counter, blogger_login, avatars, dct, cities_dct)

    @classmethod
    def update_exists_subscribers(cls, dct: dict):
        subscribers: QuerySet[Subscriber] = Subscriber.objects.filter(social_id__in=list(dct.keys()))
        for subscriber in subscribers:
            sub: Subscriber = dct[subscriber.social_id]
            change(subscriber, sub, 'avatar')
            change(subscriber, sub, 'city_id')
            change(subscriber, sub, 'country_id')
            change(subscriber, sub, 'language')
            change(subscriber, sub, 'followers')
            change(subscriber, sub, 'following')
            change(subscriber, sub, 'contents')
            change(subscriber, sub, 'bio')
            change(subscriber, sub, 'verification_type_id')
            change(subscriber, sub, 'is_business_account')
            change(subscriber, sub, 'category')
            change(subscriber, sub, 'address_id')
            if sub.bloggers[0] not in subscriber.bloggers:
                subscriber.bloggers.append(sub.bloggers[0])
            try:
                del dct[subscriber.social_id]
            except Exception as e:
                print(e)
        time_print('update count', len(subscribers))
        Subscriber.objects.bulk_update(subscribers, fields=['avatar', 'city_id', 'country_id',
                                                              'language', 'followers', 'following', 'contents',
                                                              'bio', 'verification_type_id', 'is_business_account',
                                                              'category', 'address_id'
                                                              ], batch_size=1_000)

        return dct

    @classmethod
    def flood(cls, dct: dict):
        arr = list(dct.values())
        time_print('len insert',len(arr))
        Subscriber.objects.bulk_create(arr, ignore_conflicts=True, batch_size=5_000)
