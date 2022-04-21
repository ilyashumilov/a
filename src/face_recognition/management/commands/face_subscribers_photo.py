import time

from django.core.management import BaseCommand
import asyncio

# face_subscribers_photo
from django.db.models import Q

from face_recognition.modules.Controller import Controller
from face_recognition.services.face_service import get_gender_and_age
from main.models import Subscriber
from parsing.AsyncParsingNew.utils import chunks, time_print


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


async def child(subscriber: Subscriber, controller: Controller):
    result = await get_gender_and_age(subscriber.avatar, controller)
    if result:
        subscriber.age, subscriber.gender_id = result
        subscriber.is_photo_analyzed = True
        return subscriber
    return None


async def worker():
    last_id = 0
    loop = asyncio.get_event_loop()
    controller = Controller(loop)
    only_fields = ['id', 'is_photo_analyzed', 'avatar', 'gender_id', 'age', 'avatar']

    while True:
        q = (Q(id__gt=last_id) & ~Q(avatar=None))

        subscribers = list(Subscriber.objects.filter(q).order_by('id')[:1_000].only(*only_fields))
        size = len(subscribers)
        if size == 0:
            last_id = 0
            time_print('all subs done')
            time.sleep(60 * 5)
            continue
        last_id = subscribers[-1].id

        counter_mini_subs = 0
        arr = []
        for mini_subscribers in chunks(subscribers, 100):
            results = await asyncio.gather(*[child(i, controller) for i in mini_subscribers])

            for result in results:
                if result:
                    arr.append(result)
            counter_mini_subs += 100
            time_print('counter', counter_mini_subs, 'of', size, 'arr len', len(arr), 'last_id', last_id)

        time_print('bulk update', len(arr))
        Subscriber.objects.bulk_update(arr, fields=['age', 'gender_id', 'is_photo_analyzed'])
