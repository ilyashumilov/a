import asyncio

import aiohttp
import asyncpg
import enlighten
import requests
from django.conf import settings
from django.core.management import BaseCommand

# clearer
from main.models import AccountParser, TidDone, Blogger
from parsing.AsyncParsingMulti.AsyncParsingModule import create_pbar
from parsing.AsyncParsingNew.utils import create_pool, time_print


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        asyncio.get_event_loop().run_until_complete(worker())


async def worker():
    # pass
    pool = await create_pool(settings.DATABASES['default'])
    timeout = 1
    bloggers = list(Blogger.objects.exclude(categories=[]).only('id','login'))
    counter= 0
    async with pool.acquire() as connection:
        connection: asyncpg.Connection
        await connection.execute(f"""SET statement_timeout TO {timeout}000;""")
        for i in bloggers:
            try:
                await connection.fetch(f"""SELECT (1) AS "a" FROM "parsing_subscriber" WHERE "parsing_subscriber"."bloggers" <@ ARRAY[{i.id}]::bigint[] LIMIT 1""")
                counter+=1
                time_print(i.login,i.id,counter)
            except Exception as e:
                pass
    time_print('subs count',counter)
