import string

from django.utils import timezone

from main.models import Blogger
from main.services import capwords
from ..extra import create_photo_link_extra, date_to_response_date_extra


def blogger_info_method(blogger: Blogger):
    return {
        "blogger_id": blogger.id,
        "avatar": blogger.avatar_link,
        "posts_count": 0,
        "likes_count": 0,
        "comments_count": 0,
        "subscribers_count": blogger.dt,
        "following_count": blogger.following,
        "age": blogger.age,
        "gender": blogger_value_with_name(blogger.gender),
        "name": blogger.name,
        "status": blogger_value_with_name(blogger.status),
        "account_creation_date": date_to_response_date_extra(blogger.account_creation_date),
        "parsing": blogger_parsing_data(blogger),
        'er12__global': blogger.er
    }


def blogger_value_with_name(blogger_field):
    if blogger_field is None:
        return None
    return blogger_field.name


def blogger_parsing_data(blogger: Blogger):
    return {
        "status": blogger.parsing_status,
        "refreshing": blogger.parsing_measurement,
        "updated_at": date_to_response_date_extra(timezone.now())
    }


GENDERS = {1: "male", 2: "female", None: None}


def another_socials(blogger: Blogger):
    data = dict(blogger.another_socials)
    another_socials = {}
    for social_name, login in data.items():
        try:
            blg = Blogger.objects.select_related('social_network_type').get(login=login,
                                                                            social_network_type__name=social_name)
            t = another_socials[social_name] = {}
            blogger_info_to_dct(blg, t)
        except:
            pass
    return another_socials


def blogger_info_to_dct(blg: Blogger, dct: dict):
    dct['login'] = capwords(blg.login)
    dct['photo'] = blg.avatar_link
    dct['name'] = blg.name_capitalized
    dct['category'] = blg.category
    dct['gender'] = GENDERS[blg.gender_id]
    dct['default_total'] = blg.dt
    dct['er'] = blg.er
