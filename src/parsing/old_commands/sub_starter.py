import time

from django.core.management import BaseCommand

# sub_starter
from main.models import Blogger
from parsing.ParsingModules.SubscriberModule import SubscriberModule


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def worker():
    tv = SubscriberModule()
    tv.automate_create_task()

