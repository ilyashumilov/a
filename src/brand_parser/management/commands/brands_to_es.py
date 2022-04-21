from django.core.management import BaseCommand
from elasticsearch import Elasticsearch

es = Elasticsearch()
INDEX = "brand-index"

# brands_to_es
from brand_parser.models import Brand


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def add_brand_elastic(brand: Brand):
    doc = {'id': brand.id, 'name': brand.name}
    res = es.index(index=INDEX, body=doc)
    print(res)


def worker():
    brands = Brand.objects.all()
    for brand in brands:
        add_brand_elastic(brand)
        print(brand.id)
