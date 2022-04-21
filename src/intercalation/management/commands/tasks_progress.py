import time

import requests
from django.conf import settings
from django.core.management import BaseCommand

# tasks_progress
from django.db.models import Q

from flood.models import ParsingTaskMicroservice, ParsingTaskBloggerStatus
from parsing.AsyncParsingNew.utils import chunks, time_print


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def get_data(tasks_ids):
    url = f'{settings.MICROSERVICE_IP}/api/progress/'
    # url = f'http://127.0.0.1:8000/api/result/1/'
    response = requests.post(url, json={'tasks_ids': tasks_ids}).json()
    if isinstance(response, dict):
        return response
    return {'data': {}}


def get_error_data(tasks_ids):
    url = f'{settings.MICROSERVICE_IP}/api/error/'
    # url = f'http://127.0.0.1:8000/api/result/1/'
    response = requests.post(url, json={'tasks_ids': tasks_ids}).json()
    if isinstance(response, dict):
        return response
    return {'data': []}


def progress_data_process(dct):
    data = get_data(list(dct)).get('data')
    arr = []
    for k in dct:
        if k in data:
            progress = data[k]
            obj = dct[k]
            obj.progress = progress
            arr.append(obj)
    ParsingTaskMicroservice.objects.bulk_update(arr, fields=['progress'])
    time_print('updated', len(arr))


def error_data_process(dct):
    data = get_error_data(list(dct)).get('data')
    for i in data:
        obj: ParsingTaskMicroservice = dct[str(i)]
        obj.status = ParsingTaskBloggerStatus.error
    ParsingTaskMicroservice.objects.bulk_update(list(dct.values()), fields=['status'])


def worker():
    q = (Q(status=ParsingTaskBloggerStatus.in_process) & ~Q(parser_task_id=None))
    while True:
        tasks = list(ParsingTaskMicroservice.objects.filter(q).only('id', 'parser_task_id', 'progress'))
        for mini_tasks in chunks(tasks, 1000):
            dct = {}
            for i in mini_tasks:
                i: ParsingTaskMicroservice
                dct[str(i.parser_task_id)] = i
            print(list(dct.keys())[:50])
            progress_data_process(dct)
            error_data_process(dct)

        time.sleep(60)
