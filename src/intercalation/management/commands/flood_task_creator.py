from django.core.management import BaseCommand
import asyncio

# flood_task_creator
from flood.models import ParsingTaskBloggerStatus, ParsingTaskMicroservice, ParsingTaskTypeName
from intercalation.work_modules.TaskCreator import TaskCreator
from parsing.ParsingModules.ParsingModule import time_print


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


async def pool_worker(task_type):
    task_type_name, task_type_value = task_type
    print(task_type)

    task_type_value = int(task_type_value)
    status = ParsingTaskBloggerStatus.not_started
    last_id = 0
    while True:
        tasks = list(ParsingTaskMicroservice.objects.filter(status=status, task_type_id=task_type_value,
                                                            id__gt=last_id)[:100])
        size = len(tasks)
        if size:
            last_id = tasks[-1].id
        else:
            last_id = 0
            await asyncio.sleep(10)

        print(task_type, 'len tasks', len(tasks))
        for task in tasks:
            if task.data is not None and len(task.data['items']) == 0:
                task.status = ParsingTaskBloggerStatus.error
                task.save()
                continue

            while True:
                try:
                    await TaskCreator.async_post_method(task)
                    s = f"task name {task_type_name}, task: {task}"
                    time_print(s)
                    break
                except Exception as e:
                    print(e, task_type_name, str(task.data)[:400])
                    await asyncio.sleep(1)
        await asyncio.sleep(10)
        if len(tasks) > 0:
            time_print(f"task name {task_type_name} tasks done")


async def worker():
    task_types = [(i.name, i.value) for i in ParsingTaskTypeName]

    print(task_types)
    await asyncio.gather(*[pool_worker(x) for x in task_types])
