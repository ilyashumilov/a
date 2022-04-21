import asyncio
import os
import time
from datetime import datetime
from typing import List
import django

from tortoise_base import SubscriberAsync, SubscriberToBlogger


import asyncpg
from asyncpg import Connection
from django.conf import settings

from main.models import Subscriber
from parsing.AsyncParsingNew import utils
from parsing.AsyncParsingNew.utils import time_print
from parsing.NovemberParsing import queries
from parsing.NovemberParsing.flood_module import FloodModule


class FloodSubscriberModule(object):

    async def prepare_flood(self, subscribers: List[SubscriberAsync], blogger_id: int):
        dct_subscribers_by_social_id = {}
        for sub in subscribers:
            dct_subscribers_by_social_id[sub.login] = sub

        exists = await SubscriberAsync.filter(login__in=list(dct_subscribers_by_social_id.keys()))
        dct_subs_by_id = {}
        for i in exists:
            dct_subs_by_id[i.id] = i.login

        exists_mtm = await SubscriberToBlogger.filter(subscriber_id__in=list(dct_subs_by_id.keys()),
                                                      blogger_id=blogger_id)
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

        print(len(to_create_mtm))
        await SubscriberToBlogger.bulk_create(to_create_mtm)

        to_create = []
        for i, v in dct_subscribers_by_social_id.items():
            to_create.append(
                SubscriberAsync(social_id=v.social_id, login=v.login, )
            )
        await SubscriberAsync.bulk_create(to_create,batch_size=10_000)
        print('flooded')

        from_created = await SubscriberAsync.filter(login__in=list(dct_subscribers_by_social_id.keys()))
        to_create_mtm = []
        for i in from_created:
            to_create_mtm.append(SubscriberToBlogger(subscriber_id=i.id, blogger_id=blogger_id))
        await SubscriberToBlogger.bulk_create(to_create_mtm)
        print('done', blogger_id)

    async def select_exists(self, social_ids: List[str]):
        pass

    async def update_subscribers(self, subscribers: List[Subscriber]):
        pass

    async def insert_subscribers(self, subscribers: List[Subscriber]):
        pass

