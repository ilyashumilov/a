import asyncio
import functools
import itertools
import re
import string
import sys
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List
from collections import Counter, defaultdict

from django.db.models import Count, QuerySet, Q, Sum, F, When, Case

from api.extra import rounder, create_photo_link
from api.models import ProceedBlogger
from api.services.brands_from_text import text_to_words, get_brands_from_array, get_brand
from api.services.extra_service import pre_data_for_percent, get_dt_from_blogger
from brand_parser.models import Brand
from brand_parser.services import accept_signs
from main.models import Post, Subscriber, Blogger, Comment, Emotion
from dateutil.relativedelta import relativedelta

from main.services import daily_usd_to_rub, capwords
import emoji as Emoji

dct_global_time = {}


def get_global_time():
    summer = 0
    for k, v in dct_global_time.items():
        print(k, ':', v)
        summer += v
    print('sum::', summer)


def rounder_and_int(er: float, digits: int):
    t = round(er, digits)
    if str(t).endswith('.0'):
        return int(t)
    return t


def timeit(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        elapsed_time = time.monotonic() - start_time
        name = func.__name__

        if name not in dct_global_time:
            dct_global_time[name] = 0

        dct_global_time[name] += elapsed_time
        return result

    return new_func


def text_to_date(date_text: str):
    """Y-m-d H:i"""
    pattern = "%Y-%m-%d %H:%M"
    return datetime.strptime(date_text, pattern)


def is_date_not_in_range(post, start, end):
    if start is not None and post.date < start:
        return True
    if end is not None and post.date > end:
        return True
    return False


def post_to_dict(post: Post):

    photo = post.photos_url

    photo_url = create_photo_link(photo)

    return {'id': post.id,
            'post_id': post.post_id,
            'post_login': post.post_login,
            'post_url': f"https://www.instagram.com/p/{post.post_id}/",
            'photos_url': [photo_url],
            'text': post.text,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'time': post.date.strftime('%H:%M'),
            'date': post.date.strftime('%Y-%m-%d'),
            "__sum_likes_comments": post.likes_count + post.comments_count
            }


@timeit
def involvement_er_method(post: Post, dct: dict, start: Optional[datetime] = None, end: Optional[datetime] = None):
    """Вовлеченность аудитории"""
    if is_date_not_in_range(post, start, end):
        return

    t_date = f"{post.date.month}.{post.date.year}"
    if t_date not in dct:
        dct[t_date] = {
            'date': post.date,
            'posts_count': 0,
            'likes': 0,
            'comments': 0
        }
    t = dct[t_date]
    t['posts_count'] += 1
    t['likes'] += post.likes_count
    t['comments'] += post.comments_count


def involvement_er_method_new(post: Post, dct: dict, months: List[str]):
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


@timeit
def posts_months_method(post: Post, dct: dict, start: Optional[datetime] = None, end: Optional[datetime] = None):
    """Частота постов в месяц"""

    if is_date_not_in_range(post, start, end):
        return

    t_date = f"{post.date.month}.{post.date.year}"
    if t_date not in dct:
        dct[t_date] = {
            "posts": 0,
            "advertising_posts": 0
        }

    if len(last_advertisers_method(post, dict())):
        dct[t_date]['advertising_posts'] += 1
    else:
        dct[t_date]['posts'] += 1

    pre_data_for_percent(dct, post.date, dct[t_date]['posts'])


@timeit
def comments_by_post(post: Post, dct: dict, start: Optional[datetime] = None, end: Optional[datetime] = None):
    """Комментариев на пост"""
    if is_date_not_in_range(post, start, end):
        return

    t_date = f"{post.date.month}.{post.date.year}"

    if t_date not in dct:
        dct[t_date] = {
            'comments': 0,
            'posts_count': 0,
            'avg_comments': 0
        }
    t = dct[t_date]
    t['comments'] += post.comments_count
    t['posts_count'] += 1
    t['avg_comments'] = rounder_and_int(t['comments'] / t['posts_count'], 1)

    if 'avg_comments' not in dct:
        dct['avg_comments'] = 0
    dct['avg_comments'] += post.comments_count

    if 'count' not in dct:
        dct['count'] = 0
    dct['count'] += 1

    pre_data_for_percent(dct, post.date, dct[t_date]['comments'])


def comments_by_post_new(post: Post, dct: dict, months: List[str]):
    if months[0] not in dct:
        for month in months:
            dct[month] = {
                'comments': 0,
                'posts_count': 0,
                'avg_comments': 0
            }

    t_date = f"{post.date.month}.{post.date.year}"

    if t_date not in months:
        return

    t = dct[t_date]
    t['comments'] += post.comments_count
    t['posts_count'] += 1
    t['avg_comments'] = rounder_and_int(t['comments'] / t['posts_count'], 1)

    if 'avg_comments' not in dct:
        dct['avg_comments'] = 0

    if 'count' not in dct:
        dct['count'] = 0

    dct['avg_comments'] += post.comments_count

    dct['count'] += 1

    pre_data_for_percent(dct, post.date, dct[t_date]['comments'])


@timeit
def likes_by_post(post: Post, dct: dict, start: Optional[datetime] = None, end: Optional[datetime] = None):
    """Лайков на пост"""
    if is_date_not_in_range(post, start, end):
        return

    t_date = f"{post.date.month}.{post.date.year}"
    if t_date not in dct:
        dct[t_date] = {
            'likes': 0,
            'posts_count': 0,
            'avg_likes': 0
        }
    t = dct[t_date]
    t['likes'] += post.likes_count
    t['posts_count'] += 1
    t['avg_likes'] = rounder_and_int(t['likes'] / t['posts_count'], 1)

    if 'avg_likes' not in dct:
        dct['avg_likes'] = 0
    dct['avg_likes'] += post.likes_count

    if 'count' not in dct:
        dct['count'] = 0
    dct['count'] += 1

    pre_data_for_percent(dct, post.date, dct[t_date]['likes'])


@timeit
def likes_by_post_new(post: Post, dct: dict, months: List[str]):
    if months[0] not in dct:
        for month in months:
            dct[month] = {
                'likes': 0,
                'posts_count': 0,
                'avg_likes': 0
            }

    t_date = f"{post.date.month}.{post.date.year}"
    if t_date not in months:
        return

    t = dct[t_date]
    t['likes'] += post.likes_count
    t['posts_count'] += 1
    t['avg_likes'] = rounder_and_int(t['likes'] / t['posts_count'], 1)

    if 'avg_likes' not in dct:
        dct['avg_likes'] = 0
    dct['avg_likes'] += post.likes_count

    if 'count' not in dct:
        dct['count'] = 0
    dct['count'] += 1

    pre_data_for_percent(dct, post.date, dct[t_date]['likes'])


@timeit
def best_time_to_publish(post: Post, blg: Blogger, dct: dict,
                         start: Optional[datetime] = None, end: Optional[datetime] = None):
    """Лучшее время для публикации"""
    if is_date_not_in_range(post, start, end):
        return

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
    t['er'] = calculate_er_new(t['likes_comments'], 0, blg, t['posts_count'])


@timeit
def blogger_data_method(post: Post, dct: dict):
    # dct['posts_count'] += 1
    dct['likes_count'] += post.likes_count
    dct['comments_count'] += post.comments_count


@timeit
def tags_in_posts_method(post: Post, dct: dict):
    for word in post.text.split():
        if word[0] == '#':
            hashtag = word[1:]
            if hashtag not in dct:
                dct[hashtag] = 1
            dct[hashtag] += 1


@timeit
def top_3_advertising_posts(post: Post, array: List[dict]):
    # todo заменить на поиск по @
    if len(last_advertisers_method(post, dict())) > 0:
        if len(array) < 3:
            array.append(post_to_dict(post))
            return

        for index, i in enumerate(array):
            if (i['likes_count'] + i['comments_count']) < (post.likes_count + post.comments_count):
                del array[index]
                array.append(post_to_dict(post))
                break


@timeit
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


@timeit
def last_advertisers_method_new(post: Post):
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

    return new_set


@timeit
def brand_affinity_method(post: Post, brand_affinity: dict):
    get_brands_from_array(text_to_words(post.text), brand_affinity)


def words_filter(words):
    words_new = set()
    for word in words:
        if 5 > len(word) > 20:
            continue
        if len(set(list(word)) - accept_signs) > 0:
            continue
        words_new.add(word)
    return words_new


def is_sign_exclude(word):
    for i in word:
        if i not in accept_signs:
            return True
    return False


@timeit
def text_filter(text: str, unique_words: set):
    for word in set(text.split()):
        if not check_word_exclude(word):
            unique_words.add(word)


def check_word_exclude(word: str):
    if len(word) < 5:
        return True
    if len(word) > 20:
        return True
    if is_sign_exclude(word):
        return True
    return False


def create_brands_dict(words: set):
    dct = {}

    for i in words:
        i = str(i).lower()
        if not check_word_exclude(i):
            t = get_brand(i)
            if t is not None:
                if not check_word_exclude(t['name']):
                    dct[t['id']] = t
                    if t['id'] == 3:
                        print('brand', t, i)

    brands = Brand.objects.filter(id__in=list(dct.keys()))
    new_dct = {}
    for brand in brands:
        try:
            url = brand.img.url
        except:
            url = None

        new_dct[brand.id] = {
            "id": brand.id,
            "name": capwords(brand.name),
            "photo": url
        }

    return new_dct


@timeit
def er12_method(post: Post, dct: dict, index):
    if index < 12:
        if 'likes' not in dct:
            dct['likes'] = 0
        if 'comments' not in dct:
            dct['comments'] = 0

        dct['likes'] += post.likes_count
        dct['comments'] += post.comments_count


def rounder_er12(er12, blogger, size):
    return calculate_er_new(er12['likes'], er12['comments'], blogger)


def calculate_er_new(likes: int, comments: int, blogger: Blogger, post_count=12):
    subscribers_count = blogger.dt
    if post_count == 0:
        post_count = 1

    er = (((likes + comments) / post_count) / subscribers_count) * 100

    if er > 100:
        return 100.
    return rounder(er)


def calculate_er_new__test(likes: int, comments: int, blogger: ProceedBlogger, post_count=12):
    subscribers_count = get_dt_from_blogger(blogger)
    er = (((likes + comments) / post_count) / subscribers_count) * 100
    return rounder(er)


# ProceedBlogger.objects.filter(id=1).filter().annotate(posts_likes_count=Sum('posts.likes'))
epsilon = Decimal(0.1)


def relevant_bloggers(blogger_: Blogger):
    dt = blogger_.dt
    dt_min = dt - int(dt * 0.1)
    dt_max = dt + int(dt * 0.1)

    q = (Q(social_network_type_id=blogger_.social_network_type_id) & Q(default_total__gte=dt_min) & Q(
        default_total__lte=dt_max))

    bloggers_simple = Blogger.objects.filter(q & Q(categories__overlap=blogger_.categories)) \
        .annotate(likes_count=Sum(Case(When(posts__is_deleted=False, then=F('posts__likes_count')))))
    if len(bloggers_simple) == 0:
        bloggers_simple = Blogger.objects.filter(q).annotate(
            likes_count=Sum(Case(When(posts__is_deleted=False, then=F('posts__likes_count')))))

    bloggers_simple.prefetch_related('posts')

    result = []
    for blogger in bloggers_simple:
        avatar = blogger.avatar
        try:
            avatar = blogger.avatar_link
        except:
            pass

        if blogger_.id == blogger.id:
            continue

        if blogger.likes_count is None:
            blogger.likes_count = 0
        er=blogger.create_er()
        if er is not None:
            er=float(er)

        result.append([
            blogger.login,
            blogger.name,
            blogger.likes_count,
            blogger.dt,
            avatar,
            er

        ])
    result = sorted(result, key=lambda x: (x[2], x[3]), reverse=True)
    return result


def calculate_price(blogger: Blogger, avg_likes, avg_comments):
    # return (get_dt_from_blogger(blogger) // 10000) * 10 * 71
    dollar = daily_usd_to_rub()
    one_activity_cost = 0.1
    return round((avg_likes + avg_comments) / blogger.post_default_count * one_activity_cost * dollar)


def create_avatar_photo_link(blogger: ProceedBlogger):
    try:
        return create_photo_link(blogger.avatar)
    except:
        return None


@timeit
def posts_by_day(post: Post, dct: dict, start: Optional[datetime] = None, end: Optional[datetime] = None):
    """Частота постов в день на протяжении времени"""

    if is_date_not_in_range(post, start, end):
        return

    t_date = f"{post.date.day}.{post.date.month}.{post.date.year}"
    if t_date not in dct:
        dct[t_date] = {
            "posts": 0,
            "advertising_posts": 0
        }

    if "@" in post.text:
        dct[t_date]['advertising_posts'] += 1
    else:
        dct[t_date]['posts'] += 1


def rm_all_not_symb_in_text(text) -> str:
    return_text = []
    reject_symbs = set(list('.,-—'))

    for symb in text:
        if symb in Emoji.UNICODE_EMOJI['en'] or symb in reject_symbs:
            return_text.append(' ')
        else:
            return_text.append(symb)

    return (''.join(return_text)).strip().replace('  ', ' ').strip()


@timeit
def words_in_bio_subscribers(subscribers: QuerySet[Subscriber]):
    dct = {}
    bios = subscribers.exclude(bio=None).only('bio').values_list('bio', flat=True)

    for bio in bios:

        bio: str
        bio_ = rm_all_not_symb_in_text(bio)

        text_dct = Counter(bio_.strip().lower().split())

        for key, value in text_dct.items():
            if len(key) <= 2:
                continue
            if key not in dct:
                dct[key] = value
            else:
                dct[key] += value

    new_dct = {}
    for i, v in dct.items():
        if v > 1:
            new_dct[i] = v

    new_dct = dict(sorted(new_dct.items(), key=lambda item: item[1], reverse=True))
    return dict(itertools.islice(new_dct.items(), 50))


def by_comments(comments: List[Comment], emotions_graph, posts_date, emotions_dct, emoji, profanity_dct):
    size = 0
    try:
        st = time.monotonic()
        counter = 0
        for comment in comments:
            comment: Comment

            t_graph = emotions_graph[posts_date[comment.post_id]]

            t_graph['comments_count'] += 1
            try:
                t_graph[emotions_dct[comment.emotion_text_type_id]] += 1
            except:
                pass

            for k, v in comment.emoji.items():
                if k not in emoji:
                    emoji[k] = v
                else:
                    emoji[k] += v

            if comment.is_contain_profanity is True:
                profanity_dct['use'] += 1
            elif comment.is_contain_profanity is False:
                profanity_dct['not_use'] += 1
            size += 1
            counter += 1

    except Exception as e:
        print(e)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    use_and_not_use_count = profanity_dct['use'] + profanity_dct['not_use']

    print('use', profanity_dct['use'] / use_and_not_use_count)
    print('not_use', profanity_dct['not_use'] / use_and_not_use_count)

    profanity_dct['use'] = rounder_and_int(profanity_dct['use'] / use_and_not_use_count, 2) * 100
    profanity_dct['not_use'] = rounder_and_int(profanity_dct['not_use'] / use_and_not_use_count, 2) * 100

    # return emotions_graph, emoji, profanity_dct


@timeit
def comment_graph(posts: QuerySet[Post]):
    posts_date = {}
    emoji = {}
    emotions_graph = {}
    profanity_dct = {"use": 0, "not_use": 0}

    emotions_dct = {}
    for i in Emotion.objects.all():
        emotions_dct[i.id] = i.name

    for post in posts:
        t_date = f"{post.date.month}.{post.date.year}"
        posts_date[post.id] = t_date
        emotions_graph[t_date] = dict(comments_count=0, positive=0, neutral=0, negative=0)

    comments = Comment.objects.filter(
        Q(post_id__in=list(posts_date.keys())) & Q(is_done=True) & ~Q(emotion_text_type=None)) \
        .only('emotion_text_type_id', 'emoji', 'post_id', 'is_contain_profanity')

    st = time.monotonic()
    print(len(comments))
    print('end time comments', time.monotonic() - st)

    by_comments(comments, emotions_graph, posts_date, emotions_dct, emoji, profanity_dct)

    emoji = dict(sorted(emoji.items(), key=lambda item: item[1], reverse=True))
    emoji = dict(itertools.islice(emoji.items(), 50))

    return emotions_graph, emoji, profanity_dct


def get_last_months(number: int):
    months = []
    for i in range(number):
        t = datetime.today() - relativedelta(months=i)
        months.append(f'{t.month}.{t.year}')
    return months


def sql_result_none_checking(result: tuple):
    t = []
    for i in result:
        if i is None:
            t.append(0)
        else:
            t.append(i)
    return tuple(t)


def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return 0
