import asyncio
import os
import time

from django.conf import settings
from django.core.management import BaseCommand

# db_configure
from dotenv import load_dotenv, find_dotenv

from main.models import Subscriber
from parsing.AsyncParsingNew.utils import create_pool, execute_sql, time_print, select_one


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


async def worker():
    # await db_init(settings.DATABASES['default'])
    # st=time.monotonic()
    # a = await SubscriberAsync.filter().limit(100).offset(100000)
    # print(len(a))
    # print(time.monotonic()-st)
    #
    # return
    db = {
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get('DB_PASSWORD'),
        "HOST": os.environ.get('DB_HOST'),
        "NAME": os.environ.get('DB_NAME')
    }
    t = 0
    pool = await create_pool(db)
    # for i in range(0, 1_000_000):
    # ids = list(Subscriber.objects.filter(social_type_id=1).values_list('social_id', flat=True)[:1000])
    # Subscriber.objects.filter(social_id__in=ids, social_type_id=3)

    try:
        time_print('starteed')
        sql = f"""CREATE INDEX "subscriber_address_id_index_06_0134617" ON "public"."parsing_subscriber" USING BTREE ("address_id");"""
        res = await select_one(pool, sql)
        time_print('done', sql)
        # time_print('doner', 'index', 'i', i,'res',res)
    except Exception as e:
        print(e)
