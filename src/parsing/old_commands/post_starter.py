import time

from django.core.management import BaseCommand


# post_starter
from parsing.ParsingModules.PostModule import PostModule


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def worker():
    tv = PostModule()
    tv.automate_create_task()
