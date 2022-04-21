import asyncio
import sys
from datetime import datetime, timedelta

import asyncpg
import gspread
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from django.conf import settings
from django.core.management import BaseCommand

# google_sheet
from django.db.models import Q

from flood.models import ParsingTaskBlogger, ParsingTaskBloggerStatus
from main.models import Blogger, Post
from main.predict_utils import update_cell_on_index, get_date_index, predict
from parsing.AsyncParsingNew import utils
from parsing.AsyncParsingNew.utils import chunks


COUNT_BLOGGERS_QUERY = """SELECT count(*) FROM (SELECT blogger_id FROM {} GROUP by blogger_id) x"""
COUNT_QUERY = """SELECT count(*) FROM {}"""


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())
        scheduler = AsyncIOScheduler()
        scheduler.add_job(worker, 'interval', minutes=60, replace_existing=True)
        scheduler.start()
        loop.run_forever()


async def sheet1(sheet: gspread.Spreadsheet, pool: asyncpg.Pool):
    worksheet = sheet.worksheet("Лист1")
    index = get_date_index(worksheet)

    bloggers_count = await utils.select_one(pool, COUNT_BLOGGERS_QUERY.format('hype__post'))
    posts_count = await utils.select_one(pool, COUNT_QUERY.format('hype__post'))

    update_cell_on_index(index, 2, bloggers_count, worksheet)
    update_cell_on_index(index, 3, posts_count, worksheet)

    worksheet = sheet.worksheet("Лист1")

    update_cell_on_index(5, 8, predict(3, worksheet), worksheet)
    update_cell_on_index(5, 9, predict(4, worksheet), worksheet)


async def sheet2(sheet: gspread.Spreadsheet, pool: asyncpg.Pool):
    worksheet = sheet.worksheet("Лист2")
    index = get_date_index(worksheet)

    count_bloggers = Blogger.objects.filter(social_network_type_id=3).count()
    count_subscribers = await utils.select_one(pool,
                                               "SELECT reltuples::bigint FROM pg_catalog.pg_class WHERE relname = 'hype__subscriber';")

    update_cell_on_index(index, 2, count_bloggers, worksheet)
    update_cell_on_index(index, 3, count_subscribers, worksheet)

    worksheet = sheet.worksheet("Лист2")

    update_cell_on_index(5, 8, predict(3, worksheet), worksheet)
    update_cell_on_index(5, 9, predict(4, worksheet), worksheet)


async def sheet5(sheet: gspread.Spreadsheet, pool: asyncpg.Pool):
    worksheet = sheet.worksheet("Лист5")
    start = datetime.now() - timedelta(days=7)

    done_bloggers_all = ParsingTaskBlogger.objects.filter(Q(status=ParsingTaskBloggerStatus.in_process) | Q(status=ParsingTaskBloggerStatus.done)).count()
    blgs_count = Blogger.objects.filter(Q(social_network_type_id=3) & ~Q(categories=[3])).count()
    posts_count = Post.objects.count()
    count_subscribers = await utils.select_one(pool,
                                               "SELECT reltuples::bigint FROM pg_catalog.pg_class WHERE relname = 'hype__subscriber';")

    index = get_date_index(worksheet)
    update_cell_on_index(index, 2, done_bloggers_all, worksheet)
    update_cell_on_index(index, 3, count_subscribers, worksheet)
    update_cell_on_index(index, 4, posts_count, worksheet)
    update_cell_on_index(index, 5, blgs_count, worksheet)
    update_cell_on_index(index, 6, done_bloggers_all, worksheet)


async def worker():
    gc = gspread.service_account(filename="credentials.json")
    sheet = gc.open_by_url(
        "https://docs.google.com/spreadsheets/d/1yPb5NTCXUVPq9u1MGk14sfKpcemQeXo0n7qKDSWcXWI/edit#gid=0")
    pool = await utils.create_pool(settings.DATABASES['default'])

    try:
        await sheet2(sheet, pool)
        print('sheet2 done')

    except Exception as e:
        print('sheet2', e)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    try:
        await sheet5(sheet, pool)
        print('sheet5 done')
    except Exception as e:
        print('sheet5', e)
    try:
        await sheet1(sheet, pool)
        print('sheet1 done')

    except Exception as e:
        print('sheet1', e)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
