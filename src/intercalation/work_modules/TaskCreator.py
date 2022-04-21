import aiohttp
import requests
from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone

from flood.models import ParsingTaskBlogger, ParsingTaskMicroservice, ParsingTaskTypeName, ParsingTaskBloggerStatus, \
    ParsingTaskBloggerType
from main.models import Post, Blogger
from parsing.AsyncParsingNew.utils import chunks


class TaskCreator:
    url = f"{settings.MICROSERVICE_IP}/api/tasks/"

    @classmethod
    def __choose_methods(cls, parsing_task_blogger):
        cls.filtering_bloggers(parsing_task_blogger, [parsing_task_blogger.get_blogger_login()])
        cls.posts(parsing_task_blogger)

    #     todo кнопка обновить

    @classmethod
    def create_parsing_task(cls, blogger: Blogger = None):
        result = ParsingTaskBlogger.objects.create(blogger=blogger, day=timezone.now().date(),
                                                   status=ParsingTaskBloggerStatus.in_process,
                                                   task_type=ParsingTaskBloggerType.one_time
                                                   )
        return result, True

    @classmethod
    def full_parsing(cls, blogger: Blogger):
        result, created = cls.create_parsing_task(blogger)
        cls.__choose_methods(result)
        return result, created

    @classmethod
    def __create_parsing_microservice(cls, parsing_task_blogger: ParsingTaskBlogger,
                                      task_type: ParsingTaskTypeName, data: list,
                                      **kwargs):
        obj = ParsingTaskMicroservice(task_blogger=parsing_task_blogger,
                                      task_type_id=task_type.value,
                                      task_type_name=task_type.name,
                                      parser_task_id=None,
                                      status=ParsingTaskBloggerStatus.not_started,
                                      data={'items': data},
                                      **kwargs
                                      )
        return obj

    @classmethod
    def clean_items(cls, task_microservice: ParsingTaskMicroservice):
        items = task_microservice.data['items'].copy()
        task_microservice.data['items'] = list(filter(lambda x: len(x) > 0, items))
        if len(task_microservice.data['items']) != len(items):
            task_microservice.save(update_fields=['data'])

    @classmethod
    def pre_post_method(cls, task_microservice: ParsingTaskMicroservice, **kwargs):
        cls.clean_items(task_microservice)
        if task_microservice.extra_info is None:
            task_microservice.extra_info = {}

        body = {
            "data": task_microservice.data,
            "task_type_id": task_microservice.task_type_id,
            "priority": 1,
            "special_save_type": "csv",
            **task_microservice.extra_info
        }
        return body

    @classmethod
    async def async_post_method(cls, parsing_task_microservice: ParsingTaskMicroservice):
        body = TaskCreator.pre_post_method(parsing_task_microservice)
        async with aiohttp.ClientSession() as session:
            async with session.post(TaskCreator.url, json=body) as response:
                data = await response.json()
        return cls.after_post_method(parsing_task_microservice, data['task_id'])

    @classmethod
    def sync_post_method(cls, parsing_task_microservice: ParsingTaskMicroservice):
        body = TaskCreator.pre_post_method(parsing_task_microservice)
        response = requests.post(f"{settings.MICROSERVICE_IP}/api/tasks/", json=body, timeout=99999)
        data = response.json()
        return cls.after_post_method(parsing_task_microservice, data['task_id'])

    @classmethod
    def after_post_method(cls, parsing_task_microservice: ParsingTaskMicroservice, task_id):
        parsing_task_microservice.parser_task_id = task_id
        parsing_task_microservice.status = ParsingTaskBloggerStatus.in_process
        parsing_task_microservice.save(update_fields=['parser_task_id', 'status'])
        return True

    @classmethod
    def subscribers(cls, parsing_task_blogger: ParsingTaskBlogger, **kwargs):
        task_type = ParsingTaskTypeName.subscribers
        data = [parsing_task_blogger.blogger.login]
        obj = TaskCreator.__create_parsing_microservice(parsing_task_blogger, task_type, data, extra_info=kwargs)
        obj.save()
        return obj

    @classmethod
    def subscriber_not_detail(cls, parsing_task_blogger: ParsingTaskBlogger, **kwargs):
        task_type = ParsingTaskTypeName.subscribers_not_detail
        data = [parsing_task_blogger.blogger.login]
        obj = TaskCreator.__create_parsing_microservice(parsing_task_blogger, task_type, data, extra_info=kwargs)
        obj.save()
        return obj

    @classmethod
    def posts(cls, parsing_task_blogger: ParsingTaskBlogger):
        task_type = ParsingTaskTypeName.posts
        data = [parsing_task_blogger.blogger.login]
        obj = TaskCreator.__create_parsing_microservice(parsing_task_blogger, task_type, data)
        obj.save()

        return obj

    @classmethod
    def comments(cls, parsing_task_blogger: ParsingTaskBlogger, posts: QuerySet[Post], limit=None):
        task_type = ParsingTaskTypeName.comments
        url_template = 'https://www.instagram.com/p/{}/'

        tasks = []
        for post in posts:
            data = [url_template.format(post.post_id)]
            extra_info = {"post_id": post.post_id}
            if limit is not None:
                extra_info['limit'] = limit

            obj = TaskCreator.__create_parsing_microservice(parsing_task_blogger, task_type,
                                                            data, extra_info=extra_info)
            tasks.append(obj)
        ParsingTaskMicroservice.objects.bulk_create(tasks, batch_size=5_000, ignore_conflicts=True)
        return tasks

    @classmethod
    def likes(cls, parsing_task_blogger: ParsingTaskBlogger, posts: QuerySet[Post], limit=None):
        task_type = ParsingTaskTypeName.likes
        url_template = 'https://www.instagram.com/p/{}/'

        tasks = []
        for post in posts:
            data = [url_template.format(post.post_id)]
            extra_info = {"post_id": post.post_id}
            if limit is not None:
                extra_info['limit'] = limit

            obj = TaskCreator.__create_parsing_microservice(parsing_task_blogger, task_type,
                                                            data, extra_info=extra_info)
            tasks.append(obj)
        ParsingTaskMicroservice.objects.bulk_create(tasks, batch_size=5_000, ignore_conflicts=True)
        return tasks

    @classmethod
    def filtering(cls, parsing_task_blogger: ParsingTaskBlogger, array: list, chunks_support=True):
        task_type = ParsingTaskTypeName.filtering
        tasks = []
        if chunks_support:
            for data in chunks(array, 200):
                obj = TaskCreator.__create_parsing_microservice(parsing_task_blogger, task_type, data)
                tasks.append(obj)
        else:
            obj = TaskCreator.__create_parsing_microservice(parsing_task_blogger, task_type, array)
            tasks.append(obj)
        ParsingTaskMicroservice.objects.bulk_create(tasks, batch_size=5_000, ignore_conflicts=True)
        return tasks

    @classmethod
    def filtering_bloggers(cls, parsing_task_blogger: ParsingTaskBlogger, array: list, chunks_support=True, **kwargs):
        task_type = ParsingTaskTypeName.blogger_filtering
        tasks = []
        if chunks_support:
            for data in chunks(array, 100):
                obj = TaskCreator.__create_parsing_microservice(parsing_task_blogger, task_type, data, **kwargs)
                tasks.append(obj)
        else:
            obj = TaskCreator.__create_parsing_microservice(parsing_task_blogger, task_type, array, **kwargs)
            tasks.append(obj)
        ParsingTaskMicroservice.objects.bulk_create(tasks, batch_size=5_000, ignore_conflicts=True)
        return tasks
