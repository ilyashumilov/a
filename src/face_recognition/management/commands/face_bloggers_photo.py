import time

from django.core.management import BaseCommand
import asyncio


# face_bloggers_photo
from django.db.models import Q

from face_recognition.modules.Controller import Controller
from face_recognition.services.face_service import get_gender_and_age
from main.models import Blogger
from parsing.AsyncParsingNew.utils import time_print, chunks


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


async def child(blogger: Blogger, controller: Controller):
    result = await get_gender_and_age(blogger.avatar, controller)
    if result:
        blogger.age, blogger.gender_id = result
        blogger.is_photo_analyzed = True
        return blogger
    return None


async def worker():
    last_id = 0
    loop = asyncio.get_event_loop()
    controller = Controller(loop)
    only_fields = ['id', 'is_photo_analyzed', 'avatar', 'gender_id', 'age', 'avatar']

    while True:
        q = (Q(id__gt=last_id) & ~Q(avatar=None))

        bloggers = list(Blogger.objects.filter(q).order_by('id')[:1_000].only(*only_fields))
        size = len(bloggers)
        if size == 0:
            last_id = 0
            time_print('all blgs done')
            time.sleep(60 * 5)
            continue
        last_id = bloggers[-1].id

        counter_mini_subs = 0
        arr = []
        for mini_bloggers in chunks(bloggers, 100):
            results = await asyncio.gather(*[child(i, controller) for i in mini_bloggers])

            for result in results:
                if result:
                    arr.append(result)
            counter_mini_subs += 100
            time_print('counter', counter_mini_subs, 'of', size, 'arr len', len(arr), 'last_id', last_id)

        time_print('bulk update', len(arr))
        Blogger.objects.bulk_update(arr, fields=['age', 'gender_id', 'is_photo_analyzed'])
