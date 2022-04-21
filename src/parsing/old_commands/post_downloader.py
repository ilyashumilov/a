import time

from django.core.management import BaseCommand


# post_downloader
from parsing.ParsingModules.PostModule import PostModule


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def worker():
    pm = PostModule()
    while True:
        pm.done_tasks()
        time.sleep(60)
