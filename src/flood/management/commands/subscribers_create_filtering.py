import time

from django.core.management import BaseCommand
import asyncio

# subscribers_create_filtering
from django.db.models import Q

from intercalation.work_modules.TaskCreator import TaskCreator
from main.models import Subscriber
from parsing.AsyncParsingNew.utils import time_print


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


async def worker():
    last_id = 90_000_000_000
    while True:
        q = (Q(followers=None) & Q(id__lt=last_id))
        subscribers = list(Subscriber.objects.filter(q).order_by('-id')[:50_000].only('id', 'social_id'))

        size = len(subscribers)
        if size:
            last_id = subscribers[-1].id
        else:
            break
            last_id = 90_000_000_000
            time_print('last_id=0,sleep')

            time.sleep(hour * 3)

        arr = [i.social_id for i in subscribers]
        t, c = TaskCreator.create_parsing_task(None)
        TaskCreator.filtering(t, arr, chunks_support=False)
        time_print('filtering len', len(arr), 'last id', last_id)
