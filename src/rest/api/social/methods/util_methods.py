import datetime
from math import ceil

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import connection
from django.db.models import Prefetch, QuerySet
from django.http import HttpRequest

from main.models import Post


def date_to_front_date(date: datetime.date):
    try:
        return date.strftime('%Y-%m-%d')
    except:
        return None


def date_to_front_datetime(date: datetime.datetime):
    try:
        return date.strftime('%Y-%m-%d %H:%M')
    except:
        return None


def get_last_months(number: int):
    months = []
    for i in range(number):
        t = datetime.datetime.today() - relativedelta(months=i)
        months.append(f'{t.month}.{t.year}')
    return months


def get_last_month(number: int):
    return (datetime.datetime.today() - relativedelta(months=number)).date()


def get_last_month_post(posts: QuerySet[Post], number):
    date: datetime.datetime = posts[0].date
    return (date - relativedelta(months=number)).date()


def get_with_last_non_zero_months_by_sorted_posts(posts: QuerySet[Post], number: int):
    if len(posts) > 0:
        date: datetime.datetime = posts[0].date
        date_month = datetime.datetime.strptime(f'{date.month}_{date.year}', '%m_%Y')
        months = []
        for i in range(1, number + 1):
            t = date_month - relativedelta(months=i)
            months.append(f'{t.month}.{t.year}')
        return months
    else:
        return get_last_months(number)


def get_months_between_two_post(post1: Post, post2: Post):
    arr = []
    counter = 0
    while True:
        t = (post1.date - relativedelta(months=counter)).date()
        arr.append(f'{t.month}.{t.year}')
        if t <= post2.date.date():
            break

        counter += 1

    return tuple(arr)


def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return 0


def calculation_of_interest(num, count, one_hundred=True):
    t_num = num

    if count != 0:
        if one_hundred:
            num = num / count * 100
        else:
            num = num / count

    if 1 > num:
        num = ceil(num * 100) / 100.0

    if 0.1 > num > 0:
        num = 0.1

    return round(num, 2)


def my_custom_sql(sql_query):
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        rows = cursor.fetchall()

    return rows


def sql_result_none_checking(result: tuple):
    t = []
    for i in result:
        if i is None:
            t.append(0)
        else:
            t.append(i)
    return tuple(t)


def plus_or_set(dct, name, value):
    if name not in dct:
        dct[name] = 0
    dct[name] += value


def calculate_er(likes: int, comments: int, blogger, post_count=12):
    subscribers_count = blogger.dt
    if post_count == 0:
        post_count = 1

    er = (((likes + comments) / post_count) / subscribers_count) * 100

    if er > 100:
        return 100.
    return round(er, 2)


def round_(value, digits=0):
    t = round(value, digits)
    if str(t).endswith('.0'):
        return int(t)
    return t


def calculate_percent(last, first):
    if last == 0:
        last = 1
    if first == 0:
        first = 1

    t = (last / first) * 100
    t = 1 - t

    return round(t, 2)


def create_photo_link(photo: str, request: HttpRequest = None):
    if photo is None or len(str(photo)) < 2:
        return None
    host = settings.BASE_URL if request is None else request.get_host()
    return f'http://{host}/api/photo/{photo}/'


def posts_prefetch_control():
    prf = Prefetch(
        'posts',
        queryset=Post.objects.filter(is_deleted=False).order_by('-date').only('likes_count', 'comments_count',
                                                                              'blogger_id'), to_attr='posts_done'
    )
    return prf
