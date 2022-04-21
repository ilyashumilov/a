import math

from django.db.models import Q

from brand_parser.models import Brand
from main.models import Blogger
from rest.api.top.general.metrics import generate_steps, round_step

base_q = (Q(social_network_type_id=3) & Q(file_from_info__overlap=['Топ']))


def metrics():
    default_total = all_methods('default_total')
    post_default_count = all_methods('post_default_count')
    engagement_rate = er_steps()
    brands = get_brands()
    countries = get_countries()
    categories = get_categories()
    genders = get_genders()
    another_socials = ['tiktok']

    return dict(default_total=default_total, post_default_count=post_default_count, engagement_rate=engagement_rate,
                brands=brands, countries=countries, categories=categories, genders=genders,
                another_socials=another_socials
                )


def all_methods(field: str):
    max, min = get_max_and_min(field)
    steps = generate_steps(max, min)
    steps_type = ('big', 'big', 'small', 'small', 'small')
    for i, v in enumerate(steps):
        steps[i] = round_step(v, steps_type[i])
    return steps


def get_brands():
    brands = list(Blogger.objects.filter(base_q).values_list('advertisers_ids', flat=True))
    brands_dct = {}
    for i in brands:
        for j in i:
            brands_dct[j] = None

    brands = Brand.objects.filter(id__in=list(brands_dct)).only('id', 'name')
    del brands_dct
    brands_dct = {}
    for i in brands:
        brands_dct[i.name] = i.id
    return brands_dct


def get_categories():
    categories = list(
        Blogger.objects.select_related('category').filter(base_q).values_list('category__name', flat=True))
    categories = list(set(categories))
    return categories


def get_genders():
    return {"male": 1, "female": 2, "undefined": None}


def get_countries():
    return ("Испания", "Индонезия", "Польша", "Италия", "Вьетнам", "Узбекистан",
            "Азербайджан", "Германия", "Португалия", "Тайланд", "Англия", 'Россия')


def er_steps():
    max, min = get_max_and_min_er('engagement_rate')
    steps = generate_steps_er(max, min)
    steps_type = ('big', 'big', 'small', 'small', 'small')
    for i, v in enumerate(steps):
        type_ = steps_type[i]
        if type_ == 'big':
            steps[i] = math.ceil(v)
        else:
            steps[i] = math.floor(v)
    return steps

def get_max_and_min_er(field: str):
    dct = {f'{field}__gt': 0}
    q = (Q(**dct) & base_q)
    max_blogger = Blogger.objects.filter(q).order_by(f'-{field}').only(field).first()
    max = float(getattr(max_blogger, field))
    min_blogger = Blogger.objects.filter(q).order_by(f'{field}').only(field).first()
    min = float(getattr(min_blogger, field))

    return max, min

def generate_steps_er(max: float, min: float) -> list:
    t = max - min
    steps_percents = [0.75, 0.5, 0.25]
    steps = [max]
    for i in steps_percents:
        steps.append((t * i))
    steps.append(min)
    print('steps', steps)
    return steps


def get_max_and_min(field: str):
    dct = {f'{field}__gt': 0}
    q = (Q(**dct) & base_q)
    max_blogger = Blogger.objects.filter(q).order_by(f'-{field}').only(field).first()
    max = getattr(max_blogger, field)
    min_blogger = Blogger.objects.filter(q).order_by(f'{field}').only(field).first()
    min = getattr(min_blogger, field)

    return max, min
