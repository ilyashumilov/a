import requests
from django.conf import settings
from django.core.management import BaseCommand

# azer_parsing
from django.utils import timezone

from flood.models import ParsingTaskTypeName, ParsingTaskMicroservice, ParsingTaskBloggerStatus, ParsingTaskBlogger, \
    ParsingTaskBloggerType
from main.models import Blogger
from parsing.AsyncParsingNew.utils import time_print


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def post_method(task_type_id: int, items: list):
    body = {
        "data": {"items": items},
        "task_type_id": task_type_id,
        "priority": 1,
        "special_save_type": "csv",
        "limit": 10_000
    }
    response = requests.post(f"{settings.MICROSERVICE_IP}/api/tasks/", json=body, timeout=99999)
    return response.json()['task_id']


def start_parsing(blogger, parsing_task_blogger):
    task_id = post_method(ParsingTaskTypeName.subscribers.value, [blogger.social_id])
    ParsingTaskMicroservice.objects.get_or_create(task_blogger=parsing_task_blogger,
                                                  task_type_id=ParsingTaskTypeName.subscribers.value,
                                                  task_type_name=ParsingTaskTypeName.subscribers.name,
                                                  parser_task_id=task_id,
                                                  defaults={"status": ParsingTaskBloggerStatus.in_process})


def parse(blg: Blogger):
    result, cr = ParsingTaskBlogger.objects.get_or_create(blogger=blg, day=timezone.now().date(),
                                                          defaults={'status': ParsingTaskBloggerStatus.in_process,
                                                                    'task_type': ParsingTaskBloggerType.one_time
                                                                    })
    start_parsing(blg, result)


def worker():
    bloggers = Blogger.objects.filter(file_from_info="GEO Azerbaijan")
    counter = 0
    for i in bloggers:
        try:
            parse(i)
            time_print(i.login, counter)
        except Exception as e:
            print(e,'----',i.login)
        counter += 1

    print(len(bloggers))
