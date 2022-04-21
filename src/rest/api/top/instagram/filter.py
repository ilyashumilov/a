from django.contrib.postgres.search import TrigramSimilarity

from main.models import Blogger


class Filter:
    fields = ['default_total__lte', 'default_total__gte', 'post_default_count__lte', 'post_default_count__gte',
              'engagement_rate__lte', 'engagement_rate__gte', 'advertisers__overlap', 'file_from_info__overlap',
              'category_id', 'gender_id__in', 'another_socials__tiktok__isnull'
              ]

    fields_instead_of = {'country_id': 'file_from_info__overlap', 'advertiser_id': 'advertisers__overlap',
                         'gender_id': 'gender_id__in', 'another_social': 'another_socials__tiktok__isnull'
                         }

    @classmethod
    def filter(cls, request):
        data: dict = request.data
        q = {}
        for field in cls.fields:
            if field in data:
                if field in cls.fields_instead_of:
                    field = cls.fields_instead_of[field]

                q[field] = data[field]

        search__ = data.get('login', '')

        if 'name' in data and data.get('login', None) is None:
            search__ = data.get('name')

        _1 = TrigramSimilarity('login', search__, raw=True, fields=('login',))
        _2 = TrigramSimilarity('name', search__, raw=True, fields=('name',))
        vector_trigram = _1 + _2
        threshold = 0.24

        # q = dict(social_network_type_id=social_network_type_id_value)
        file_from = ['Топ']
        if 'file_from_info__overlap' in q:
            file_from.append(q['file_from_info__overlap'][0])
            del q['file_from_info__overlap']
        if 'another_socials__tiktok__isnull' in q:
            q['another_socials__tiktok__isnull'] = True

        q = {'file_from_info__overlap': file_from, 'social_network_type_id': 3}

        results = Blogger.objects.annotate(similarity=vector_trigram) \
            .filter(similarity__gt=threshold, **q).order_by('-similarity')

        by_login = Blogger.objects.select_related('category').filter(login__iexact=search__, **q)
        by_name = Blogger.objects.select_related('category').filter(name__iexact=search__, **q)

        dct = {}
        results = list(by_login) + list(by_name) + list(results)

        for i in results:
            if i.id in dct:
                continue
            else:
                dct[i.id] = i

        return list(dct.values())
