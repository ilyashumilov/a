import random
import time

import requests
from django.core.management import BaseCommand
import asyncio

# blogger_analyzer_photo
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


async def get_gender_age(blogger: Blogger, controller: Controller):
    try:
        # print(subscriber.avatar )
        photo = await controller.get_photo(blogger.avatar)
        if photo is None:
            blogger.avatar = None
            return

        dt = await controller.get_face_properties(photo)

        features = dt['faces'][0]['features']
        gender = 1 if features['gender']['gender'].lower() == 'male' else 2
        age = features['age']
        print(features)

        blogger.gender_id = gender
        blogger.age = age

    except Exception as e:
        pass

    blogger.is_photo_analyzed = True
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
        bloggers = Blogger.objects.filter(Q(is_photo_analyzed=False) & ~Q(avatar=None)) \
                       .only('is_photo_analyzed', 'avatar', 'gender_id', 'age', 'avatar')[:SUBS_LIMIT]
        size = len(bloggers)
        print('bloggers len', size)
        if size == 0:
            await asyncio.sleep(10)

        of = size // 100
        counter = 1

        for subs_arr in chunks(bloggers, CHUNKS_LIMIT):
            st = time.monotonic()
            await asyncio.gather(*[get_gender_age(i, controller) for i in subs_arr])
            time_print('photos', CHUNKS_LIMIT * counter, 'of', of, 'done time', time.monotonic() - st)
            t = random.choice(subs_arr)
            print(t.gender_id, t.age, t.id)
            counter += 1

        time_print('update,subscribers')
        Blogger.objects.bulk_update(bloggers, fields=['gender_id', 'age', 'is_photo_analyzed'],
                                    batch_size=5_000)
        await asyncio.sleep(10)
