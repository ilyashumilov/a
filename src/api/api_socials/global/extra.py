import datetime

from django.conf import settings
from django.db import connection
from django.http import HttpRequest
from math import ceil

from main.models import Blogger


def create_photo_link_extra(photo: str, request: HttpRequest = None):
    if photo is None:
        return None
    host = settings.BASE_URL if request is None else request.get_host()
    return f'http://{host}/api/photo/{photo}/'


def date_to_response_date_extra(date: datetime.date):
    try:
        return date.strftime('%Y-%m-%d')
    except:
        return None


def calculation_of_interest_extra(num, count: int, one_hundred=True):
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


def my_custom_sql_extra(sql_query):
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        rows = cursor.fetchall()

    return rows


def plus_or_set_extra(dct, name, value):
    if name not in dct:
        dct[name] = 0
    dct[name] += value


def sql_result_none_checking_extra(result: tuple):
    t = []
    for i in result:
        if i is None:
            t.append(0)
        else:
            t.append(i)
    return tuple(t)


def rounder_and_int_extra(er: float, digits: int):
    t = round(er, digits)
    if str(t).endswith('.0'):
        return int(t)
    return t


def calculate_er_new_extra(likes: int, comments: int, blogger: Blogger, post_count=12):
    if post_count == 0:
        post_count = 1

    er = (((likes + comments) / post_count) / blogger.dt) * 100
    return round(er, 2)
