from django.core.management import BaseCommand

from brand_parser.parsing import parsing_through_trademarks


class Command(BaseCommand):
    def handle(self, *args, **options):
        parsing_through_trademarks()
