import time

from django.core.management import BaseCommand

# update_btn_cron
from django.utils import timezone

from crontask.models import TaskCron
from main.models import Blogger
from parsing.AsyncParsingNew.utils import time_print


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def updater(to_add: int):
    today = timezone.now().date()
    tasks = list(TaskCron.objects.filter(created_at__day=today.day,
                                         created_at__month=today.month,
                                         created_at__year=today.year,
                                         done=False
                                         ).only('blogger', 'id', 'done','pk','id'))

    not_done = []
    done = []
    done_tasks = []

    for task in tasks:
        blogger = task.blogger

        blogger.parsing_measurement += to_add
        if blogger.parsing_measurement == 100:
            task.done = True
            blogger.parsing_status = True
            done_tasks.append(task)
            done.append(blogger)
        else:
            not_done.append(blogger)

    Blogger.objects.bulk_update(not_done, fields=['parsing_measurement'])
    Blogger.objects.bulk_update(done, fields=['parsing_status', 'parsing_measurement'])
    TaskCron.objects.bulk_update(done_tasks, fields=['done'])

    time_print('not done', len(not_done), 'done', len(done), 'done tasks', len(done_tasks))


def worker():
    while True:
        updater(5)

        time.sleep(60)
