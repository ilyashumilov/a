import sys

from django.conf import settings
from elasticsearch import Elasticsearch


def text_to_words(text: str):
    arr = []
    for i in set(text.lower().split(' ')):
        if len(i) > 3:
            arr.append(i)
    return arr


# try:
es = Elasticsearch(hosts=[settings.ELASTIC])
# except:
#     es = None
# es=None
INDEX = "brand-index"


def search_brands_via_elastic(words: list):
    try:
        for i in words:
            if search_brand_via_elastic(i):
                return True
        return False
    except Exception as e:
        return True


def search_brand_via_elastic(word: str):
    search_param = {
        'query': {
            'match': {
                'name': word
            }
        }
    }
    try:
        res = es.search(index=INDEX, body=search_param)
        for hit in res['hits']['hits']:
            return True
    except Exception as e:
        print(e)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        return False


def get_brands_from_array(words: list, brand_affinity: dict):
    for i in words:
        get_brands_via_elastic(i, brand_affinity)


def get_brands_via_elastic(word: str, brand_affinity: dict):
    search_param = {
        'query': {
            'match': {
                'name': word
            }
        }
    }
    try:
        res = es.search(index=INDEX, body=search_param)
        for hit in res['hits']['hits']:
            brand = hit['_source']
            brand_affinity[brand['id']] = brand
    except Exception as e:
        print(e)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


def get_brand(word: str):
    search_param = {
        'query': {
            'match': {
                'name': word
            }
        }
    }
    try:
        res = es.search(index=INDEX, body=search_param)
        for hit in res['hits']['hits']:
            brand = hit['_source']
            # print('----------------------')
            # print(brand)
            # print('----------------------')

            return brand
    except Exception as e:
        print(e)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception(e)
