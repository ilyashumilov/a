import time

from django.core.management import BaseCommand

# sub_downloader
from parsing.ParsingModules.SubscriberModule import SubscriberModule


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def worker():
    sm = SubscriberModule()
    while True:
        sm.done_tasks()
        time.sleep(60)
