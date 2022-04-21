import multiprocessing
import django
django.setup()
from django.core.management import BaseCommand

# post_multi
from main.models import AccountParser
from parsing.AsyncParsingMulti.AsyncPostParsing import AsyncPostParsing


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


async def work(app: AsyncPostParsing):
    await app.parser_start()


def before_async(parser_id):
    app = AsyncPostParsing(parser_id)
    app.loop.create_task(work(app))
    app.loop.run_forever()


def worker():
    parser_ids = list(AccountParser.objects.filter(account_type=1).values_list('id', flat=True))
    with multiprocessing.Pool(len(parser_ids)) as p:
        p.map(before_async, parser_ids)
