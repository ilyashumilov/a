from django.core.management import BaseCommand


# post_text
from parsing.AsyncParsingNew.AsyncPostParsing import AsyncPostParsing


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def worker():
    async def work(asp: AsyncPostParsing):
        await asp.get_parsers()

    asp = AsyncPostParsing()
    asp.loop.create_task(work(asp))
    asp.loop.run_forever()

