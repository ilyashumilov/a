import sys
import time

import requests
from django.conf import settings

from flood.models import ParsingTaskMicroservice, ParsingTaskBloggerStatus
from flood.modules.BaseFloodModel import BaseFloodModel
from flood.services.global_service import check_result
from parsing.AsyncParsingNew.utils import time_print


async def script_base_for_flood(q, class_: BaseFloodModel):
    while True:
        parsing_tasks = ParsingTaskMicroservice.objects.select_related('task_blogger', 'task_blogger__blogger') \
            .filter(q)
        for parsing_task in parsing_tasks:
            data_link = check_result(parsing_task.parser_task_id)
            time_print(parsing_task.task_blogger.blogger.login, 'data link', data_link)
            if data_link is None:
                continue
            response = requests.get(f'{settings.MICROSERVICE_IP}{data_link}')
            try:
                time_print(parsing_task.task_blogger.blogger.login, 'read data')
                if parsing_task.extra_info is None:
                    parsing_task.status = ParsingTaskBloggerStatus.error
                    parsing_task.save(update_fields=['status'])
                    continue

                await class_.from_file(response, parsing_task.extra_info['post_id'])
                time_print(parsing_task.task_blogger.blogger.login, 'done flood')
                parsing_task.status = ParsingTaskBloggerStatus.done
            except Exception as e:
                print(e)
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

                parsing_task.status = ParsingTaskBloggerStatus.error
            parsing_task.save(update_fields=['status'])
            # parsing_task.task_blogger.percent += 25
            # parsing_task.task_blogger.save(update_fields=['percent'])
            # parsing_task.task_blogger.blogger.parsing_measurement = parsing_task.task_blogger.percent
            # parsing_task.task_blogger.blogger.save(update_fields=['parsing_measurement'])

        time.sleep(10)
