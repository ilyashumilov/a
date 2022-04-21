import random
import time

import requests
from django.core.management import BaseCommand
import asyncio

# subscribers_analyzer_photo
from django.db.models import Q

from face_recognition.modules.Controller import Controller
from main.models import Subscriber, Blogger
from parsing.AsyncParsingNew.utils import chunks, time_print


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker(loop))
        # loop.create_task(worker())
        # loop.run_forever()


CHUNKS_LIMIT = 50
SUBS_LIMIT = 100


async def get_gender_age(subscriber: Subscriber, controller: Controller):
    try:
        # print(subscriber.avatar )
        photo = await controller.get_photo(subscriber.avatar)
        if photo is None:
            subscriber.avatar = None
            return subscriber

        dt = await controller.get_face_properties(photo)

        features = dt['faces'][0]['features']
        gender = 1 if features['gender']['gender'].lower() == 'male' else 2
        age = features['age']
        print(features)

        subscriber.gender_id = gender
        subscriber.age = age


    except Exception as e:
        pass

    subscriber.is_photo_analyzed = True
    return subscriber
    # return subscriber


async def worker(loop):
    controller = Controller(loop)

    # 10001041785__zwonova_marina
    # photo = await controller.get_photo("10001041785__zwonova_marina")
    # dt = await controller.get_face_properties(photo)
    # print(dt)
    #
    # return

    while True:
        subscribers = Subscriber.objects.filter(Q(is_photo_analyzed=False) & ~Q(avatar=None)) \
                          .only('pk', 'is_photo_analyzed', 'avatar', 'gender_id', 'age')[:SUBS_LIMIT]
        size = len(subscribers)
        print('subs len', size)
        if size == 0:
            await asyncio.sleep(10)

        of = size // 100
        counter = 1
        arr = []
        for subs_arr in chunks(subscribers, CHUNKS_LIMIT):
            st = time.monotonic()
            subs_after = await asyncio.gather(*[get_gender_age(i, controller) for i in subs_arr])
            arr.extend(subs_after)
            time_print('photos', CHUNKS_LIMIT * counter, 'of', of, 'done time', time.monotonic() - st)
            t = random.choice(subs_arr)
            print(t.gender_id, t.age, t.id)
            counter += 1

        time_print('update,subscribers')

        index_subs = 0
        for subs_mini in chunks(arr, 1_000):
            Subscriber.objects.bulk_update(subs_mini, fields=['gender_id', 'age', 'is_photo_analyzed', 'avatar'],
                                             batch_size=1_000)
            index_subs += 1

            time_print(len(subs_mini), 'index subs in update', index_subs)
        await asyncio.sleep(10)
