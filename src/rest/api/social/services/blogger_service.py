from django.db.models import Q, Sum, Case, When, F
from django.utils import timezone

from main.models import Blogger, Category
from rest.api.social.methods import util_methods, bloggers_methods
from rest.api.social.methods.bloggers_methods import methods_of_relevant_type, check_word, check_word_choose
from rest.api.social.services.language_controller import LanguageController
from rest.decorators import timeit


@timeit
def blogger_service(blogger: Blogger, language):
    data = {
        "blogger_id": blogger.id,
        "avatar": blogger.avatar_link,
        "posts_count": blogger.post_default_count,
        "subscribers_count": blogger.default_total,
        "following_count": blogger.following,
        "age": blogger.age,
        "gender": blogger_value_with_name(blogger.gender, language),
        "name": blogger.name_capitalized,
        "status": blogger_value_with_name(blogger.status, language),
        "account_creation_date": util_methods.date_to_front_date(blogger.account_creation_date),
        "parsing": {
            "status": blogger.parsing_status,
            "refreshing": blogger.parsing_measurement,
            "updated_at": util_methods.date_to_front_datetime(blogger.parsing_updated_at)
        },
        "__er": blogger.er,
        "er12": float(blogger.engagement_rate),
        "another_socials": another_socials(blogger, language),
        "updated_at": util_methods.date_to_front_datetime(timezone.now()),
        "relevant_bloggers": relevant_bloggers_service(blogger),
        "categories": blogger_categories(blogger, language),
        "category": blogger_value_with_name(blogger.category, language),
        "is_verify": True if (blogger.verification_type_id is not None and blogger.verification_type_id > 0) else False
    }
    return data


def blogger_value_with_name(blogger_field, language):
    if blogger_field is None:
        return None
    return LanguageController.get_field(blogger_field, language)


def gender_by_id(blogger: Blogger):
    if blogger.gender_id == 1:
        return "male"
    elif blogger.gender_id == 2:
        return "female"
    else:
        return None


def blogger_profile(blogger: Blogger, language):
    return {
        "login": blogger.login.capitalize(),
        "photo": blogger.avatar_link,
        "name": blogger.name_capitalized,
        "category": blogger_value_with_name(blogger.category, language),
        "gender": gender_by_id(blogger),
        "default_total": blogger.default_total,
        "er": float(blogger.create_er()),
        "status": blogger_value_with_name(blogger.status, language),
        "is_verify": is_blogger_verify(blogger),
        "is_advertiser": blogger.is_advertiser
    }


def is_blogger_verify(blogger: Blogger):
    verification_type_id = blogger.verification_type_id
    if verification_type_id is not None and int(verification_type_id) > 0:
        return True
    else:
        return False


SOCIALS = {
    'instagram': 3,
    'youtube': 2,
    'facebook': 0,
    'vk': 1,
    'tiktok': 5
}


# SOCIALS = {i.name.lower(): i.id for i in SocialNetwork.objects.all().only('name')}


def another_socials(blogger: Blogger, language):
    data = dict(blogger.another_socials)
    another_socials = {}
    for social_name, login in data.items():
        try:
            blg = Blogger.objects.get(login=login, social_network_type_id=SOCIALS[social_name.lower()])
            another_socials[social_name] = blogger_profile(blg, language)

        except Exception as e:
            print(e)
            pass
    return another_socials



def relevant_bloggers_service(blogger: Blogger, type_method=0):
    delta = 0.184

    pattern = check_word(blogger.name)
    checker = check_word_choose[pattern]

    q_ = methods_of_relevant_type[type_method](blogger, delta)
    q_ = Q(social_network_type_id=blogger.social_network_type_id) & Q(status_id=1) & q_

    relevant_bloggers = Blogger.objects.filter(q_).only('id', 'name')

    relevant_bloggers_ids = []

    for relevant_blogger in relevant_bloggers:

        if blogger.id == relevant_blogger.id:
            continue
        if not checker(relevant_blogger.name):
            continue

        relevant_bloggers_ids.append(relevant_blogger.id)

    relevant_bloggers = Blogger.objects.filter(id__in=relevant_bloggers_ids[:20]).annotate(
        likes_count=Sum(Case(When(posts__is_deleted=False, then=F('posts__likes_count')))))

    result = []
    for relevant_blogger in relevant_bloggers:

        if relevant_blogger.likes_count is None:
            relevant_blogger.likes_count = 0

        er = relevant_blogger.engagement_rate
        if er is not None:
            er = float(er)

        result.append([
            relevant_blogger.login,
            relevant_blogger.name,
            relevant_blogger.likes_count,
            relevant_blogger.dt,
            relevant_blogger.avatar_link,
            er,
            False if relevant_blogger.verification_type is None else True
        ])
    result = sorted(result, key=lambda x: (x[2], x[3]), reverse=True)
    return result


def blogger_categories(blogger: Blogger, language='ru'):
    field_name = LanguageController.get_field_name(language)

    categories = Category.objects.filter(id__in=blogger.categories).values_list(field_name, flat=True)
    return ', '.join(list(categories))


def blogger_gender(blogger: Blogger):
    gender = blogger.gender_id
    if gender == 1:
        return 'Мужчина'
    elif gender == 2:
        return 'Женщина'


def blogger_status(blogger: Blogger):
    status = blogger.status_id
    if status == 1 or status is None:
        return 'Открыт'
    else:
        return 'Закрыт'
