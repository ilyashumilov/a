from django.core.management import BaseCommand


# sub_text
from parsing.AsyncParsingNew.AsyncSubscriberParsing import AsyncSubscriberParsing


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def worker():
    async def work(asp: AsyncSubscriberParsing):
        await asp.get_parsers()

    asp = AsyncSubscriberParsing()
    asp.loop.create_task(work(asp))
    asp.loop.run_forever()

