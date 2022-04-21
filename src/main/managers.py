from typing import List

from django.db import connection, OperationalError
from django.db.models import Manager, QuerySet


class SubscriberManager(Manager):
    def filter_by_blogger(self, blogger_id: int):
        return self.filter_with_timeout([blogger_id])

    def filter_with_timeout(self, bloggers: List[int], timeout: int = 5):
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""SET statement_timeout TO {timeout}000;""")
                result = self.filter(bloggers__overlap=bloggers)
            return result
        except OperationalError as e:
            print(e)
            return QuerySet()

    def filter_by_bloggers(self, bloggers: List[int]):
        return self.filter_with_timeout(bloggers)


class BloggerManager(Manager):
    def get_default(self, **kwargs):
        return self.get(**kwargs, social_network_type_id=3)


class PostManager(Manager):
    def filter_default(self, blogger, **kwargs):
        return self.filter(blogger=blogger, is_deleted=False, **kwargs).order_by('-date')
