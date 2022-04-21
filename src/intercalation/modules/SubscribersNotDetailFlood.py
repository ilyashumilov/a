import typing

import requests

from intercalation.base_modules.BaseFloodModel import BaseFloodModel
from main.models import Blogger, Subscriber
from parsing.ParsingModules.ParsingModule import time_print


class SubscribersNotDetailFlood(BaseFloodModel):
    @classmethod
    async def from_file(cls, response: requests.Response, blogger_login: typing.Optional[str]):
        response.encoding = 'utf-8'
        blogger = Blogger.objects.get_default(login=blogger_login)

        dct = {}
        counter = 0
        for line_i in response.iter_lines(chunk_size=10_000, decode_unicode=True):
            try:
                social_id, login = line_i.split(':')
                dct[social_id] = login
                counter += 1

                if counter > 0 and counter % 10_000 == 0:
                    cls.process_subscribers(dct.copy(),blogger)
                    dct.clear()
            except:
                pass

        try:
            if len(dct) > 0:
                cls.process_subscribers(dct.copy(), blogger)
                dct.clear()
        except:
            pass

    @classmethod
    def process_subscribers(cls, dct: dict, blogger: Blogger):
        exists_subscribers = Subscriber.objects.filter(social_network_type_id=3, social_id__in=list(dct))
        time_print(blogger.login,'exists_subscribers',len(exists_subscribers))
        arr = []
        for exist_subscriber in exists_subscribers:
            flag = False
            new_subscriber_login = dct[exist_subscriber.social_id]
            if exist_subscriber.login != new_subscriber_login:
                exist_subscriber.login = new_subscriber_login
                flag = True

            if blogger.id not in exist_subscriber.bloggers:
                exist_subscriber.bloggers.append(blogger.id)
                flag = True

            if flag:
                arr.append(exist_subscriber)

            del dct[exist_subscriber.social_id]

        Subscriber.objects.bulk_update(arr, fields=['login', 'bloggers'], batch_size=1_000)
        time_print(blogger.login, 'upd subs', len(arr))

        cls.insert_subscribers(dct, blogger)

    @classmethod
    def insert_subscribers(cls, dct: dict, blogger: Blogger):
        arr = []
        for social_id, login in dct.items():
            arr.append(
                Subscriber(social_network_type_id=3, social_id=social_id,
                           login=login, bloggers=[blogger.id])
            )
        Subscriber.objects.bulk_create(arr, batch_size=5_000)
        time_print(blogger.login, 'insert subs', len(arr))

