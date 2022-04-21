import sys

import requests
from django.conf import settings

from flood.models import ParsingTaskTypeName, ParsingTaskMicroservice, ParsingTaskBloggerStatus
from intercalation.base_modules.BaseFloodModel import BaseFloodModel
from intercalation.base_modules.ParsingTaskMicroserviceConsumer import ParsingTaskMicroserviceConsumer
from parsing.AsyncParsingNew.utils import time_print


class FloodCommand:
    def __init__(self, parsing_task_type_name: ParsingTaskTypeName):
        self.parsing_consumer = ParsingTaskMicroserviceConsumer(parsing_task_type_name,
                                                                ['task_blogger', 'task_blogger__blogger'])
        self.base_parser = BaseFloodModel

    async def cron_monitoring(self):
        # todo create monitor via apscheduler
        pass

    async def flood_data(self):
        for i, dct in self.parsing_consumer.loop_consume():
            parsing_task: ParsingTaskMicroservice = dct[i['task']]
            log_data = parsing_task.task_blogger.blogger.login
            await self.main_flood(i, parsing_task, log_data)

    async def main_flood(self, i, parsing_task, log_data):
        # log_data - parsing_task.task_blogger.blogger.login

        data_link = i['link']

        if data_link is None:
            return
        response = requests.get(f'{settings.MICROSERVICE_IP}{data_link}')

        try:
            time_print(log_data, 'read data')
            await self.base_parser.from_file(response, log_data)
            time_print(log_data, 'done flood')
            parsing_task.status = ParsingTaskBloggerStatus.done
        except Exception as e:
            print(e)
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e,
                  'task', parsing_task.id)
            print(response.text[:20].replace('\n', ' '))
            parsing_task.status = ParsingTaskBloggerStatus.error
        parsing_task.save(update_fields=['status'])
