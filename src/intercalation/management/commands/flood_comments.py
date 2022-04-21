from django.core.management import BaseCommand
import asyncio


# flood_comments
from flood.models import ParsingTaskTypeName, ParsingTaskMicroservice
from intercalation.modules.CommentsFlood import CommentsFlood
from intercalation.base_modules.FloodCommand import FloodCommand


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


class FloodComments(FloodCommand):
    def __init__(self, parsing_task_type_name: ParsingTaskTypeName):
        super(FloodComments, self).__init__(parsing_task_type_name)
        self.base_parser = CommentsFlood

    async def flood_data(self):
        for i, dct in self.parsing_consumer.loop_consume():
            parsing_task: ParsingTaskMicroservice = dct[i['task']]
            log_data = parsing_task.extra_info['post_id']
            await self.main_flood(i, parsing_task, log_data)


async def worker():
    fc = FloodComments(ParsingTaskTypeName.comments)
    await fc.flood_data()
