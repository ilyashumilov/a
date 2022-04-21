import asyncio
import os
from typing import List

import django

from parsing.AsyncParsingNew.utils import time_print
from tortoise_base import SubscriberAsync, SubscriberToBlogger

from main.models import Subscriber


def got(first_value, second_value):
    if second_value is not None:
        return second_value
    return first_value


class FloodSubscriberDopModule(object):

    async def prepare_flood(self, subscribers: List[SubscriberAsync], blogger_id: int):
        dct_subscribers_by_social_id = {}
        for sub in subscribers:
            dct_subscribers_by_social_id[sub.login] = sub

        exists = await SubscriberAsync.filter(login__in=list(dct_subscribers_by_social_id.keys()))
        dct_subs_by_id = {}
        flag = True
        flagg = True
        print('exists',len(exists))

        for i in exists:
            t = dct_subscribers_by_social_id[i.login]
            dct_subs_by_id[i.id] = i.login
            i.country_id = t.country_id
            i.city_id = t.city_id
            i.language = t.language
            if i.city_id is not None and flag:
                print('city_id',i.city_id, i,i.id)
                flag = False
            if i.country_id is not None and flagg:
                print('country_id',i.country_id, i,i.id)
                flagg = False
            await i.save()

        exists_mtm = await SubscriberToBlogger.filter(subscriber_id__in=list(dct_subs_by_id.keys()),
                                                      blogger_id=blogger_id)
        print('exists_mtm',len(exists_mtm))
        for i in exists_mtm:

            try:
                del dct_subscribers_by_social_id[dct_subs_by_id[i.subscriber_id]]
            except Exception as e:
                pass
            try:
                del dct_subs_by_id[i.subscriber_id]
            except:
                pass
        to_create_mtm = []
        for i, v in dct_subs_by_id.items():
            to_create_mtm.append(SubscriberToBlogger(subscriber_id=i, blogger_id=blogger_id))
            try:
                del dct_subscribers_by_social_id[v]
            except:
                pass

        time_print('to_create_mtm', len(to_create_mtm))
        await SubscriberToBlogger.bulk_create(to_create_mtm)

        to_create = []
        for i, v in dct_subscribers_by_social_id.items():
            to_create.append(
                SubscriberAsync(social_id=v.social_id, login=v.login, city_id=v.city_id,
                                country_id=v.country_id, language=v.language)
            )
        time_print('to create',len(to_create))
        await SubscriberAsync.bulk_create(to_create)

        from_created = await SubscriberAsync.filter(login__in=list(dct_subscribers_by_social_id.keys()))
        to_create_mtm = []
        for i in from_created:
            to_create_mtm.append(SubscriberToBlogger(subscriber_id=i.id, blogger_id=blogger_id))
        await SubscriberToBlogger.bulk_create(to_create_mtm)
        time_print('done', blogger_id)

    async def select_exists(self, social_ids: List[str]):
        pass

    async def update_subscribers(self, subscribers: List[Subscriber]):
        pass

    async def insert_subscribers(self, subscribers: List[Subscriber]):
        pass
