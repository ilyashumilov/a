import random

from django.conf import settings
from django.core.management import BaseCommand
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from brand_parser.models import Brand

es = Elasticsearch(hosts=[settings.ELASTIC])
INDEX = 'brand-index'


# brand_elastic
class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def clear():
    indices = list(es.indices.get_alias().keys())
    for index in indices:
        es.indices.delete(index=index, ignore=[400, 404])
    print('deleted')


brands = list(Brand.objects.all())


def push():
    es.indices.create(index=INDEX)

    def gendata():
        for brand in brands:
            yield {
                "_index": INDEX,
                "id": brand.id,
                "name": brand.name,
            }

    bulk(es, gendata())


def get():
    brand = random.choice(brands)
    print(brand.id, brand.name)
    print('searched:\n\n(')
    search_param = {
        'query': {
            'match': {
                'name':brand.name
            }
        }
    }
    res = es.search(index=INDEX, body=search_param)
    for hit in res['hits']['hits']:
        brand = hit['_source']
        print(brand)
    print(')')

def worker():
    get()
