import re
import string
from datetime import datetime
from typing import List

from dateutil.relativedelta import relativedelta

from main.models import Post, Blogger
from ..extra import create_photo_link_extra, date_to_response_date_extra, rounder_and_int_extra, calculate_er_new_extra


def get_last_months(number: int):
    months = []
    for i in range(number):
        t = datetime.today() - relativedelta(months=i)
        months.append(f'{t.month}.{t.year}')
    return months


def pre_dicts_create_method():
    months = get_last_months(6)
    involvement_er_dict = {}
    posts_months_dict = {}
    comments_by_post_dict = {}
    likes_by_post_dict = {}
    best_time_to_publish_dct = {}
    the_most_popular_posts = []
    tags_in_posts = {}
    er12 = {}
    words = set()

    return (
        months, involvement_er_dict, posts_months_dict, comments_by_post_dict, likes_by_post_dict,
        best_time_to_publish_dct, the_most_popular_posts, tags_in_posts, er12, words)


def involvement_er_method(post: Post, dct: dict, months: list):
    if months[0] not in dct:
        for month in months:
            dct[month] = {
                'date': post.date,
                'posts_count': 0,
                'likes': 0,
                'comments': 0
            }

    t_date = f"{post.date.month}.{post.date.year}"
    if t_date not in months:
        return

    t = dct[t_date]
    t['posts_count'] += 1
    t['likes'] += post.likes_count
    t['comments'] += post.comments_count


def posts_months_method(post: Post, dct: dict):
    t_date = post.date_str
    if t_date not in dct:
        dct[t_date] = {
            "posts": 0,
            "advertising_posts": 0
        }

    if len(last_advertisers_method(post, dict())):
        dct[t_date]['advertising_posts'] += 1
    else:
        dct[t_date]['posts'] += 1


def comments_by_post_method(post: Post, dct: dict, months: list):
    if months[0] not in dct:
        for month in months:
            dct[month] = {
                'comments': 0,
                'posts_count': 0,
                'avg_comments': 0
            }

    t_date = post.date_str

    if t_date not in months:
        return

    t = dct[t_date]
    t['comments'] += post.comments_count
    t['posts_count'] += 1
    t['avg_comments'] = rounder_and_int_extra(t['comments'] / t['posts_count'], 1)

    if 'avg_comments' not in dct:
        dct['avg_comments'] = 0

    if 'count' not in dct:
        dct['count'] = 0

    dct['avg_comments'] += post.comments_count

    dct['count'] += 1


def likes_by_post_method(post: Post, dct: dict, months: list):
    if months[0] not in dct:
        for month in months:
            dct[month] = {
                'likes': 0,
                'posts_count': 0,
                'avg_likes': 0
            }

    t_date = post.date_str
    if t_date not in months:
        return

    t = dct[t_date]
    t['likes'] += post.likes_count
    t['posts_count'] += 1
    t['avg_likes'] = rounder_and_int_extra(t['likes'] / t['posts_count'], 1)

    if 'avg_likes' not in dct:
        dct['avg_likes'] = 0
    dct['avg_likes'] += post.likes_count

    if 'count' not in dct:
        dct['count'] = 0
    dct['count'] += 1


def best_time_to_publish_method(post: Post, blogger: Blogger, dct: dict):
    t_date = f"{post.date.strftime('%A')};{post.date.hour}:00"
    if t_date not in dct:
        dct[t_date] = {
            "posts_count": 0,
            "er": 0,
            "likes_comments": 0,
            "likes": 0,
            "comments": 0,
        }
    t = dct[t_date]

    t['posts_count'] += 1
    t['likes_comments'] += (post.likes_count + post.comments_count)
    t['likes'] += post.likes_count
    t['comments'] += post.comments_count
    t['er'] = calculate_er_new_extra(t['likes_comments'], 0, blogger, t['posts_count'])


def likes_comments_method(post: Post, dct: dict):
    dct['posts_count'] += 1
    dct['likes_count'] += post.likes_count
    dct['comments_count'] += post.comments_count


def tags_in_posts_method(post: Post, dct: dict):
    for word in post.text.split():
        if word[0] == '#':
            hashtag = word[1:]
            if hashtag not in dct:
                dct[hashtag] = 1
            dct[hashtag] += 1


def text_filter_method(post: Post, unique_words: set):
    for word in set(post.text.split()):
        if not check_word_exclude(word):
            unique_words.add(word)


def top_3_advertising_posts_method(post: Post, array: List[dict]):
    if len(last_advertisers_method(post, dict())) > 0:
        if len(array) < 3:
            array.append(post_to_dict(post))
            return

        for index, i in enumerate(array):
            if (i['likes_count'] + i['comments_count']) < (post.likes_count + post.comments_count):
                del array[index]
                array.append(post_to_dict(post))
                break


def er12_method(post: Post, dct: dict, index: int):
    if index < 12:
        if 'likes' not in dct:
            dct['likes'] = 0
        if 'comments' not in dct:
            dct['comments'] = 0

        dct['likes'] += post.likes_count
        dct['comments'] += post.comments_count


# usually methods-----

accept_signs = (string.ascii_lowercase + "абвгдеёжзийклмнопрстуфхцчшщъыьэюя" + '-_—.,"' + string.digits)
accept_signs = set(list(accept_signs))


def last_advertisers_method(post: Post, set_: dict):
    def clean(text: str):
        return text.replace('・', ' ').strip().lower().split(' ')[0].split('⠀')[0].replace('@', '')

    def match(text, alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя,')):
        return not alphabet.isdisjoint(text.lower())

    t = set([clean(re.sub(r"@+", "@", k)) for k in set([re.sub(r"(\W+)$", "", j, flags=re.UNICODE) for j in
                                                        set([i for i in post.text.split() if
                                                             i.startswith("@")])])])
    new_set = dict()
    for i in t:
        if len(i) < 100 and not match(i):
            new_set[i] = 0

    return {**set_, **new_set}


def check_word_exclude(word: str):
    if len(word) < 5:
        return True
    if len(word) > 20:
        return True
    if is_sign_exclude(word):
        return True
    return False


def is_sign_exclude(word):
    for i in word:
        if i not in accept_signs:
            return True
    return False


def post_to_dict(post: Post):
    photo_url = create_photo_link_extra(post.photos_url)

    return {'id': post.id,
            'post_id': post.post_id,
            'post_login': post.post_login,
            'post_url': f"https://www.instagram.com/p/{post.post_id}/",
            'photos_url': [photo_url],
            'text': post.text,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'time': post.date.strftime('%H:%M'),
            'date': post.date.strftime('%Y-%m-%d')
            }
