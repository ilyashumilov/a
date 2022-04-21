from django.core.management import BaseCommand

# last_6_months
from django.db.models import Q

from intercalation.work_modules.TaskCreator import TaskCreator
from main.models import Blogger, Post
from parsing.AsyncParsingNew.utils import time_print
from rest.api.social.methods.util_methods import get_last_months


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def worker():
    q = Q()
    bloggers = Blogger.objects.filter(q)
    last_months = tuple(get_last_months(6))
    for blogger in bloggers:
        posts = Post.objects.filter_default(blogger).only('id', 'post_id', 'date')
        posts_comments = []

        for post in posts:
            if post.date_str in last_months:
                posts_comments.append(post)

        t, c = TaskCreator.create_parsing_task(blogger)
        TaskCreator.comments(t, posts_comments, 250)
        time_print('posts', len(posts), 'after dates', len(posts_comments))

