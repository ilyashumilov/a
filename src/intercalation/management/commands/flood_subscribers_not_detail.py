from django.core.management import BaseCommand
import asyncio


# flood_subscribers_not_detail
from flood.models import ParsingTaskTypeName, ParsingTaskMicroservice
from intercalation.base_modules.FloodCommand import FloodCommand
from intercalation.modules.SubscribersNotDetailFlood import SubscribersNotDetailFlood


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


class FloodSubscribersNotDetail(FloodCommand):
    def __init__(self, parsing_task_type_name: ParsingTaskTypeName):
        super(FloodSubscribersNotDetail, self).__init__(parsing_task_type_name)
        self.base_parser = SubscribersNotDetailFlood

    async def flood_data(self):
        for i, dct in self.parsing_consumer.loop_consume():
            parsing_task: ParsingTaskMicroservice = dct[i['task']]
            log_data = parsing_task.get_blogger_login()
            # log data #warning#

            await self.main_flood(i, parsing_task, log_data)


async def worker():
    # parsing type name #warning
    fc = FloodSubscribersNotDetail(ParsingTaskTypeName.subscribers_not_detail)
    await fc.flood_data()
