from typing import List

from brand_parser.models import Brand
from main.models import Blogger, Category
from rest.api.social.services.blogger_service import is_blogger_verify, blogger_gender, blogger_status
from rest.api.top.instagram.metrics import get_countries


def blogger_to_dict(blogger: Blogger, categories: dict, brands: dict):
    return {
        "id": blogger.id,
        "is_verify": is_blogger_verify(blogger),
        "name": blogger.name,
        "social_network_type_id": blogger.social_network_type_id,
        "post_default_count": blogger.post_default_count,
        "default_total": blogger.default_total,
        "following": blogger.following,
        "avatar": blogger.avatar_link,
        "bio": blogger.bio,
        "external_link": blogger.external_link,
        "categories": blogger.categories,
        "gender": blogger_gender(blogger),
        "status": blogger_status(blogger),
        "country": country_method(blogger),
        "category": category_method(blogger, categories),
        'another_socials': blogger.another_socials,
        "advertisers": brand_method(blogger, brands),
        "engagement_rate": float(blogger.engagement_rate if blogger.engagement_rate is not None else 0)

    }


def country_method(blogger: Blogger):
    countries = get_countries()
    for i in blogger.file_from_info:
        if i in countries:
            return i


def categories_method(bloggers: list):
    categories = [i.category_id for i in bloggers]
    categories = Category.objects.filter(id__in=categories)
    categories_dct = {None:None}
    for i in categories:
        categories_dct[i.id] = i.native_name
    return categories_dct


def brands_method(bloggers: List[Blogger]):
    brands_ids = []
    for i in bloggers:
        brands_ids.extend(i.advertisers_ids)
    brands_ids = list(set(brands_ids))
    brands = Brand.objects.filter(id__in=brands_ids)
    brands_dct = {None:None}
    for i in brands:
        brands_dct[i.id] = i.native_name
    return brands_dct


def category_method(blogger: Blogger, categories):
    return categories[blogger.category_id]


def brand_method(blogger: Blogger, brands: dict):
    brands_list = []
    for i in blogger.advertisers_ids:
        brands_list.append(brands[i])
    return brands_list


def instagram_serializer(bloggers: List[Blogger]):
    categories = categories_method(bloggers)
    brands = brands_method(bloggers)
    bloggers_array = []
    for blogger in bloggers:
        bloggers_array.append(blogger_to_dict(blogger, categories, brands))
    return bloggers_array
