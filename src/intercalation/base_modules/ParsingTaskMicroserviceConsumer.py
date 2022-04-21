import time

from django.db.models import Q

from flood.models import ParsingTaskTypeName, ParsingTaskBloggerStatus, ParsingTaskMicroservice
from flood.services.global_service import check_results


class ParsingTaskMicroserviceConsumer:
    def __init__(self, parsing_type: ParsingTaskTypeName, fields_select_related):
        self.q = (Q(status=ParsingTaskBloggerStatus.in_process) & Q(task_type_id=parsing_type.value))
        self.fields_select_related = fields_select_related
        self.only_fields = ['task_blogger.blogger', 'parser_task_id', 'status', 'extra_info']

    def consume(self):
        dct = {}
        parsing_tasks = ParsingTaskMicroservice.objects.select_related(*self.fields_select_related) \
            .filter(self.q).defer('data').order_by('-id')

        for p in parsing_tasks:
            dct[p.parser_task_id] = p
        if len(parsing_tasks) != 0:
            print('tasks parsing', len(parsing_tasks))

        while True:
            try:
                data = check_results(list(dct.keys()))
                break
            except Exception as e:
                print('connection error', e)
                time.sleep(10)
        size = len(data)
        if size != 0:
            print('task len got', size)
        for i in data:
            yield i, dct
        time.sleep(5)

    def loop_consume(self):
        while True:
            for i in self.consume():
                yield i
