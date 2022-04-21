from django.core.management import BaseCommand
import asyncio

# flood_filtering_bloggers
from flood.models import ParsingTaskTypeName, ParsingTaskMicroservice
from intercalation.modules.FilteringBloggersFlood import FilteringBloggersFlood
from intercalation.base_modules.FloodCommand import FloodCommand


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


class FloodBloggers(FloodCommand):
    def __init__(self, parsing_task_type_name: ParsingTaskTypeName):
        super(FloodBloggers, self).__init__(parsing_task_type_name)
        self.base_parser = FilteringBloggersFlood

    async def flood_data(self):
        for i, dct in self.parsing_consumer.loop_consume():
            parsing_task: ParsingTaskMicroservice = dct[i['task']]
            log_data = parsing_task.extra_info
            await self.main_flood(i, parsing_task, log_data)


async def worker():
    fc = FloodBloggers(ParsingTaskTypeName.blogger_filtering)
    await fc.flood_data()
