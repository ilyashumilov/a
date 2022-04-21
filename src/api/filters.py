import django_filters
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q, F

from main.models import Blogger


def unique_queryset(list_of_data: list):
    new_list = []
    exists_ids = set()
    for i in list_of_data:
        if i.id in exists_ids:
            continue
        exists_ids.add(i.id)
        new_list.append(i)
    return new_list


class CustomBloggerFilter:
    fields = ['social_network_type_id', 'default_total__lte', 'default_total__gte', 'gender__name',
              'engagement_rate__gte', 'engagement_rate__lte', 'age__gte', 'age__lte']

    @staticmethod
    def filter(request):
        data: dict = request.data
        q = {}
        for field in CustomBloggerFilter.fields:
            if field in data:
                q[field] = data[field]
        if 'name' in data and data.get('login', None) is None:
            q['name__search'] = data['name']
        results = Blogger.objects.filter(**q).order_by(F('default_total').desc(nulls_last=True))
        if 'login' in data and data.get('name', None) is None:
            login = data['login']
            results = list(results.filter(login=login)) + \
                      list(results.filter(login__startswith=login)) + \
                      list(results.filter(login__icontains=login))
            results = unique_queryset(results)
        if data.get('login', None) is not None and data.get('name', None) is not None:
            results = list(results.filter(Q(login__icontains=data.get('login')) | Q(name__search=data.get('name'))))

        return results

    @staticmethod
    def filter_v2(request):
        # CREATE EXTENSION IF NOT EXISTS pg_trgm
        data: dict = request.data
        q = {}
        for field in CustomBloggerFilter.fields:
            if field in data:
                q[field] = data[field]

        search = data.get('login', '')

        if 'name' in data and data.get('login', None) is None:
            search = data.get('name')

        _1 = TrigramSimilarity('login', search, raw=True, fields=('login',))
        _2 = TrigramSimilarity('name', search, raw=True, fields=('name',))
        vector_trigram = _1 + _2
        threshold = 0.3

        results = Blogger.objects.annotate(similarity=vector_trigram) \
            .filter(similarity__gt=threshold, **q).order_by('-similarity')
        return results

    @staticmethod
    def filter_v3(request):
        data: dict = request.data
        q = {}
        for field in CustomBloggerFilter.fields:
            if field in data:
                q[field] = data[field]

        search__ = data.get('login', '')

        if 'name' in data and data.get('login', None) is None:
            search__ = data.get('name')

        _1 = TrigramSimilarity('login', search__, raw=True, fields=('login',))
        _2 = TrigramSimilarity('name', search__, raw=True, fields=('name',))
        vector_trigram = _1 + _2
        threshold = 0.24

        # q = dict(social_network_type_id=social_network_type_id_value)
        q = {}
        for field in CustomBloggerFilter.fields:
            if field in data:
                q[field] = data[field]


        results = Blogger.objects.select_related('address').annotate(similarity=vector_trigram) \
            .filter(similarity__gt=threshold, **q).order_by('-similarity')

        by_login = Blogger.objects.select_related('address').filter(login__iexact=search__, **q)
        by_name = Blogger.objects.select_related('address').filter(name__iexact=search__, **q)

        dct = {}
        results = list(by_login) + list(by_name) + list(results)

        for i in results:
            if i.id in dct:
                continue
            else:
                dct[i.id] = i

        return list(dct.values())


def docs():
    return """{
        'login': {
            'type': 'str',
            'doc': 'логин'
        },
        'name': {
            'type': 'str',
            'doc': 'имя'
        },
        'social_network_type_id': {
            'type': 'int',
            'doc': 'Номер социальной сети, instagram = 3, tiktok = 5'
        },
        'default_total_gte': {
            'type': 'int',
            'doc': 'x >= filter, больше чем'
        },
        'default_total_lte': {
            'type': 'int',
            'doc': 'x <= filter, меньше чем'
        },
        'gender__name': {
            'type': 'str',
            'doc': 'пол: male, female'
        },
        'engagement_rate__gte': {
            'type': 'int',
            'doc': 'x >= filter, больше чем'
        },
        'engagement_rate__lte': {
            'type': 'int',
            'doc': 'x <= filter, меньше чем'
        },
        'age__gte': {
            'type': 'int',
            'doc': 'x >= filter, больше чем'
        },
        'age__lte': {
            "type": 'int',
            'doc': 'x <= filter, меньше чем'
        },
        'sort_by': {
            "type": "CharField",
            "doc": 'Выбор из: {"engagement_rate", "-engagement_rate", "subscribers_count", "-subscribers_count"}, 
            где - это по убыванию'
        }
    }"""
