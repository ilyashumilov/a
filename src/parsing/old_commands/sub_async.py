import asyncio
import time

from django.core.management import BaseCommand

# sub_downloader
from parsing.AsyncParsingModules.SubscriberModule import SubscriberModule


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.create_task(worker())
        loop.run_forever()


async def worker():
    sm = SubscriberModule()
    await sm.init_db()


    while True:
        await sm.done_tasks()
        time.sleep(60)
