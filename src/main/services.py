from functools import lru_cache

import requests
from django.utils import timezone
from rest_framework.generics import get_object_or_404

from crontask.models import TaskCron
from intercalation.work_modules.TaskCreator import TaskCreator
from main.models import Blogger, Post


# 0 - post, 1 - subs


def create_new_parsing_microservice(blogger_login, social_network_type_id=3):
    blogger = get_object_or_404(Blogger, login=blogger_login, social_network_type_id=social_network_type_id)

    today = timezone.now()

    if blogger.parsing_updated_at.date() == today.date():
        return {'message': "Сегодня уже был обновлен"}

    blogger.parsing_measurement = 0
    blogger.parsing_updated_at = today

    result, created = TaskCreator.full_parsing(blogger)
    TaskCron.objects.create(blogger_id=blogger.id)

    print(result)
    # WorkInfoLogs.objects.create(text=f'{blogger_login} result: {result}, created: {created}')

    blogger.save(update_fields=['parsing_measurement', 'parsing_updated_at'])
    message = {'message': f"Блогер: {blogger_login} добавлен на перепарсинг"}
    return message


def get_from_request(value: list, is_digit=False):
    if value is None:
        return None

    v: str = value[0]
    if is_digit and v.isdigit():
        return int(v)
    return v


@lru_cache()
def daily_usd_to_rub():
    try:
        resp = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
        return resp['Valute']['USD']['Value']
    except:
        return 76


def calculate_engagement_rate(blogger):
    posts = Post.objects.filter(blogger=blogger).only('likes_count', 'comments_count').order_by('-date')[:12]
    likes = 0
    comments = 0
    for i in posts:
        likes += i.likes_count
        comments += i.comments_count

    er = (((likes + comments) / 12) / blogger.dt) * 100
    return round(er, 2)


def capwords(line: str):
    try:
        return line[0].upper() + line[1:]
    except:
        return line
