import asyncio
import os
import time
from datetime import datetime
from typing import List

from django.db.models import Q

from main.management.commands.flood import chunks
from parsing.NovemberParsing.url_to_s3 import UrlToS3
from tortoise_base import SubscriberAsync, SubscriberToBlogger, PostAsync

import asyncpg
from asyncpg import Connection
from django.conf import settings

from main.models import Subscriber, Post
from parsing.AsyncParsingNew import utils
from parsing.AsyncParsingNew.utils import time_print
from parsing.NovemberParsing import queries
from parsing.NovemberParsing.flood_module import FloodModule


class FloodPostModule(object):

    async def prepare_flood(self, posts: List[PostAsync], blogger_id, social_id: str):
        ids_dct = {}
        photo_dct = {}
        upd_counter = 0
        create_counter = 0

        for i in posts:
            ids_dct[i.post_id] = i
            if i.photos_url.__contains__('.mp4'):
                photo_dct[i.photos_url] = f'{i.post_id}__{social_id}.mp4'
                i.photos_url = f'{i.post_id}__{social_id}.mp4'
            else:
                photo_dct[i.photos_url] = f'{i.post_id}__{social_id}'
                i.photos_url = f'{i.post_id}__{social_id}'

        for ph in chunks(list(photo_dct.keys()), 100):
            dct = {}
            for i in ph:
                dct[i] = photo_dct[i]

            await UrlToS3.downloader(dct)

        exists = await PostAsync.filter(post_id__in=list(ids_dct.keys()))
        ids_dct_copy = ids_dct.copy()
        for i in exists:
            t = ids_dct[i.post_id]
            i.photos_url = t.photos_url.replace(r'\u0026', '&')
            i.likes_count = t.likes_count
            i.comments_count = t.comments_count
            i.is_deleted = False
            upd_counter += 1
            await i.save()
            try:
                del ids_dct[i.post_id]
            except:
                pass
        to_create = []
        for v in ids_dct.values():
            create_counter += 1
            await v.save()
            # to_create.append(v)
        # print(,len(to_create))
        time_print('remove deleted')
        post_to_remove = Post.objects.filter(Q(blogger_id=blogger_id) & (~Q(post_id__in=list(ids_dct_copy.keys()))))
        print('post_to_remove', len(post_to_remove))
        for i in post_to_remove:
            i.is_deleted = True
        t = Post.objects.bulk_update(post_to_remove, fields=['is_deleted'])
        print('deleted', t)

        return upd_counter, create_counter

    #     f"{post['shortcode']}__{blogger.social_id}"

    async def select_exists(self, social_ids: List[str]):
        pass

    async def update_subscribers(self, subscribers: List[Subscriber]):
        pass

    async def insert_subscribers(self, subscribers: List[Subscriber]):
        pass
