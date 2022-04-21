from django.db.models import F
from django.utils import timezone

from crontask.models import TaskCron
from main.models import Blogger


def update_measurement(to_add: int):
    butch_size = 10_000
    today = timezone.now().date()
    tasks = list(TaskCron.objects.filter(created_at__day=today.day,
                                         created_at__month=today.month,
                                         created_at__year=today.year,
                                         done=False
                                         ).only('blogger', 'id', 'done'))

    size = len(tasks)
    i = 0
    for task in tasks:
        blogger = task.blogger
        not_done = []
        done = []
        done_tasks = []

        blogger.parsing_measurement += to_add
        if blogger.parsing_measurement == 100:
            task.done = True
            blogger.parsing_status = True
            done_tasks.append(tasks)
            done.append(blogger)
        else:
            not_done.append(blogger)

    while i < size:
        final_stage_bloggers = Blogger.objects.filter(parsing_measurement__gte=100 - to_add).prefetch_related(
            "cron_tasks").order_by('id')[i:i + butch_size]

        final_stage_bloggers.update(parsing_measurement=100, parsing_status=True, cron_tasks__done=True)

        i += butch_size

    i = 0
    size = Blogger.objects.filter(parsing_measurement__lte=100 - to_add).count()
    while i < size:
        not_so_final_stage_bloggers = Blogger.objects.filter(parsing_measurement__lte=100 - to_add).prefetch_related(
            "cron_tasks")[i:i + butch_size]

        not_so_final_stage_bloggers.update(parsing_measurement=F("parsing_measurement") + to_add)

        i += butch_size
