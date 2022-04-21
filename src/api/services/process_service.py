import string
import time

from django.db.models import QuerySet

from api.extra import create_photo_link
from api.services import methods, extra_service, best_service
from api.services.extra_service import pre_data_for_percent, calculate_percent, calculate_percent_new
from api.services.methods import rounder_and_int
from main.models import Post, Blogger
from main.services import capwords


def process_involvement_er_method(post_query, blogger, dct: dict, months):
    avg_er = 0
    for key, value in dct.items():
        if key in ('min', 'max'):
            continue
        er = methods.calculate_er_new(value['likes'], value['comments'], blogger)
        avg_er += er
        pre_data_for_percent(dct, value['date'], er)
        posts_count = value['posts_count'] if value['posts_count'] > 0 else 1

        value['avg_likes'] = methods.rounder_and_int(value['likes'] / posts_count, 1)
        value['avg_comments'] = methods.rounder_and_int(value['comments'] / posts_count, 1)
        value['er'] = methods.rounder_and_int(avg_er, 2)
        del value['date']

    dct['avg_er'] = methods.rounder(avg_er / (len(dct) - 2))

    last_not_zero_month = 1
    for i in months[::-1]:
        if dct[i]['er'] > 0:
            last_not_zero_month = dct[i]['er']
            break

    dct['percent'] = calculate_percent_new(dct, dct[months[0]]['er'], last_not_zero_month)
    return dct


def process_post_months_method(post_query, dct: dict = None, start=None, end=None):
    if dct is None:
        dct = {}
        for post in post_query:
            methods.posts_months_method(post, dct, start, end)

    return dct


def process_comments_by_post(post_query, dct: dict, months):
    dct['avg_comments'] = rounder_and_int(dct.get('avg_comments', 1) / dct.get('count', 1), 1)
    # dct['percent'] = calculate_percent(dct)

    last_not_zero_month = 1
    for i in months[::-1]:
        if dct[i]['avg_comments'] > 0:
            last_not_zero_month = dct[i]['avg_comments']
            break
    dct['percent'] = calculate_percent_new(dct, dct[months[0]]['avg_comments'], last_not_zero_month)
    return dct


def process_likes_by_post(post_query, dct: dict, months):
    dct['avg_likes'] = rounder_and_int(dct.get('avg_likes', 1) / dct.get('count', 1), 1)

    last_not_zero_month = 1
    for i in months[::-1]:
        if dct[i]['avg_likes'] > 0:
            last_not_zero_month = dct[i]['avg_likes']
            break
    dct['percent'] = calculate_percent_new(dct, dct[months[0]]['avg_likes'], last_not_zero_month)
    return dct


def process_best_time_to_publish(post_query, blogger, dct: dict = None, start=None, end=None, blogger_data=None):
    if dct is None:
        dct = {}
        for post in post_query:
            methods.best_time_to_publish(post, blogger, dct, start, end)
    if blogger_data is None:
        blogger_data = {
            "posts_count": 0,
            "likes_count": 0,
            "comments_count": 0
        }
        for v in dct.values():
            blogger_data['posts_count'] += v['posts_count']
            blogger_data['likes_count'] += v['likes']
            blogger_data['comments_count'] += v['comments']
    dct['test_min'] = {'test_likes': -1, 'test_comments': -1, 'test_er': -1}
    dct['test_max'] = {'test_likes': -1, 'test_comments': -1, 'test_er': -1}

    for i, v in dct.items():
        if i in ('test_min', 'test_max'):
            continue

        t_posts_count_coefficient = v['posts_count'] / blogger_data['posts_count']
        t_likes_count_coefficient = v['likes'] / blogger_data['likes_count']
        t_comments_count_coefficient = v['comments'] / blogger_data['comments_count']

        t_er_coefficient = t_likes_count_coefficient + t_comments_count_coefficient

        t_likes_count_coefficient = methods.rounder(t_posts_count_coefficient + t_likes_count_coefficient)
        t_comments_count_coefficient = methods.rounder(t_posts_count_coefficient + t_comments_count_coefficient)
        t_er_coefficient = methods.rounder(t_posts_count_coefficient + t_er_coefficient)

        calculate_test_max_min(dct, 'test_likes', t_likes_count_coefficient)
        calculate_test_max_min(dct, 'test_comments', t_comments_count_coefficient)
        calculate_test_max_min(dct, 'test_er', t_er_coefficient)

        dct[i]['test_likes'] = t_likes_count_coefficient
        dct[i]['test_comments'] = t_comments_count_coefficient
        dct[i]['test_er'] = t_er_coefficient

    return dct


def process_best_time_to_publish_new(dct: dict, posts_count: int, likes: int, comments: int, er: float):
    dct['work_data'] = {
        "max_posts": 0,
        "max_likes": 0,
        "max_comments": 0,
        "max_er": 0
    }
    work_keys = list(dct['work_data'].keys())

    for i, v in dct.items():
        if i == 'work_data':
            continue
        coeff_posts = methods.divide(v['posts_count'], posts_count)
        coeff_likes = methods.divide(v['likes'], likes)
        coeff_comments = methods.divide(v['comments'], comments)
        coeff_er = methods.divide(v['er'], er)

        best_service.best_comparison_max(dct, 'max_posts', coeff_posts)
        best_service.best_comparison_max(dct, 'max_likes', coeff_likes)
        best_service.best_comparison_max(dct, 'max_comments', coeff_comments)
        best_service.best_comparison_max(dct, 'max_er', coeff_er)

    best_service.create_steps(dct['work_data'].keys(), dct, 5)

    for i, v in dct.items():
        if i == 'work_data':
            continue
        coeff_posts = methods.divide(v['posts_count'], posts_count)
        coeff_likes = methods.divide(v['likes'], likes)
        coeff_comments = methods.divide(v['comments'], comments)
        coeff_er = methods.divide(v['er'], er)

        coeffs = dict(max_posts=coeff_posts, max_likes=coeff_likes, max_comments=coeff_comments, max_er=coeff_er)

        for key in work_keys:
            right_key = key.split('_')[1]
            steps = dct['work_data'][f'{key}__steps']

            for step_index in range(len(steps) - 1):
                if steps[step_index] < coeffs[key] <= steps[step_index + 1]:
                    dct[i][f'{right_key}_step'] = step_index + 1
                    break
    return dct


def calculate_test_max_min(dct, name: str, coeff: str):
    if dct['test_min'][name] > coeff or dct['test_min'][name] == -1:
        dct['test_min'][name] = coeff
    if dct['test_max'][name] < coeff:
        dct['test_max'][name] = coeff


def process_top_3_advertising_posts(post_query, words_brands: dict):
    st = time.monotonic()
    array = []
    words_brands_set = set()
    for v in words_brands.values():
        words_brands_set.add(v['name'])

    for post in post_query:
        for i in methods.text_to_words(post.text):
            if i in words_brands_set:

                if len(array) < 3:
                    array.append(methods.post_to_dict(post))
                    break

                for index, j in enumerate(array):
                    if (j['likes_count'] + j['comments_count']) < (post.likes_count + post.comments_count):
                        array[index] = methods.post_to_dict(post)

    print("process_top_3_advertising_posts", time.monotonic() - st)
    return array


def process_last_advertiser_new(blogger, posts: QuerySet[Post]):
    dct = {}
    new_dct = {}
    arr = []
    for post in posts:
        t_dct = methods.last_advertisers_method_new(post)
        for n in t_dct.keys():
            if n == blogger.login:
                continue
            dct[n] = {'login': capwords(str(n)), 'photo': None, 'category': ""}
            arr.append(n)
    t_blgs = Blogger.objects.select_related('status').prefetch_related('posts').filter(social_network_type_id=3,
                                                                                       login__in=arr)
    advertisers_dct = {}
    for i in t_blgs:
        advertisers_dct[i.login] = i
    # advertisers = Blogger.objects.filter(login__in=list(dct.keys()), social_network_type_id=3)
    for i in arr:
        try:
            advertiser = advertisers_dct[i]
            if advertiser.login == blogger.login:
                continue
            t = {}
            t['login'] = capwords(advertiser.login)
            t['photo'] = create_photo_link(advertiser.avatar)
            t['name'] = advertiser.name_capitalized
            t['category'] = advertiser.category
            gender = None
            if advertiser.gender == 'f':
                gender = 'female'
            elif advertiser.gender == 'm':
                gender = 'male'
            t['gender'] = gender
            t['default_total'] = advertiser.default_total
            t['er'] = advertiser.er
            t['status'] = getattr(advertiser.status, 'name', None)

            new_dct[advertiser.login] = t
        except:
            pass

    return new_dct
