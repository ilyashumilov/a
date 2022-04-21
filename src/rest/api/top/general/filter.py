from django.contrib.postgres.search import TrigramSimilarity

from main.models import Blogger


class Filter:
    fields = ['default_total__lte', 'default_total__gte', 'post_default_count__lte', 'post_default_count__gte']

    @classmethod
    def filter(cls, request):
        data: dict = request.data
        q = {}
        for field in cls.fields:
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
        q = {'file_from_info__overlap': ['Топ']}
        for field in cls.fields:
            if field in data:
                q[field] = data[field]

        results = Blogger.objects.annotate(similarity=vector_trigram) \
            .filter(similarity__gt=threshold, **q).order_by('-similarity')

        by_login = Blogger.objects.filter(login__iexact=search__, **q)
        by_name = Blogger.objects.filter(name__iexact=search__, **q)

        dct = {}
        results = list(by_login) + list(by_name) + list(results)

        for i in results:
            if i.id in dct:
                continue
            else:
                dct[i.id] = i

        return list(dct.values())
