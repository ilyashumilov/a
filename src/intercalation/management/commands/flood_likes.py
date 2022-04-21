import asyncio

from django.core.management import BaseCommand

# flood_likes
from flood.models import ParsingTaskTypeName, ParsingTaskMicroservice
from intercalation.base_modules.FloodCommand import FloodCommand
from intercalation.modules.LikesFlood import LikesFlood


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


class FloodLikes(FloodCommand):
    def __init__(self, parsing_task_type_name: ParsingTaskTypeName):
        super(FloodLikes, self).__init__(parsing_task_type_name)
        self.base_parser = LikesFlood

    async def flood_data(self):
        for i, dct in self.parsing_consumer.loop_consume():
            parsing_task: ParsingTaskMicroservice = dct[i['task']]
            log_data = parsing_task.extra_info['post_id']
            await self.main_flood(i, parsing_task, log_data)


async def worker():
    fc = FloodLikes(ParsingTaskTypeName.likes)
    await fc.flood_data()
