import asyncio
import platform

import aiohttp
from django.core.management import BaseCommand

# parser
from brand_parser import services
from brand_parser.models import Brand


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


async def fetch(url, session: aiohttp.ClientSession, index):
    resp = await session.get(url)
    print(resp.real_url, resp.url)

    return await resp.text(encoding='utf-8')


async def parser_urls():
    url = 'https://companies.rbc.ru/search/?capital_from=100000&query=&registration_date_from=1999&sorting=last_year_revenue_desc&page={}'
    brands = set()
    session = aiohttp.ClientSession()
    for index in range(1, 51):
        content = await fetch(url.format(index), session, index)
        if content is False:
            print(content)
            break

        __brands = services.parse_html(content)

        if __brands:
            brands = brands | __brands
            print(index, [i for i in __brands])
            print(len(brands), index)
        else:
            break
    await session.close()
    print(brands)
    return [Brand(name=i) for i in brands]


def check_platform():
    if platform.system() == "Windows":
        return False
    else:
        return True


def worker():
    loop = asyncio.get_event_loop()

    brands = loop.run_until_complete(parser_urls())
    print(len(brands))
    Brand.objects.bulk_create(brands, ignore_conflicts=False)
