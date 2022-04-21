import json

import requests
from django.conf import settings
from django.core.management import BaseCommand

# inf_
from django.db.models import F, Q

from main.models import Blogger, Post
from parsing.AsyncParsingNew.utils import time_print
from rest.api.social.methods.posts_methods import coverage_method, \
    advertisement_price_method, involvement_method, metrics_method
from rest.api.social.methods.util_methods import get_last_months


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def worker():
    title = "логин;подписки;кол-во постов;ср лайки;ср комменты;охват;цена за пост;вовлеченность\n"
    bloggers = Blogger.objects.filter(Q(social_network_type_id=3) & ~Q(categories=[])).order_by(
        F('default_total').desc(nulls_last=True))
    with open('bloggers_20k_26_02.csv', 'w', encoding='utf-8') as f:
        f.write(title)

    months = get_last_months(6)
    for blogger in bloggers:
        try:
            following = blogger.following
            posts = Post.objects.filter_default(blogger).only('likes_count', 'comments_count', 'blogger_id', 'date')
            dct__ = metrics_method(posts, blogger)
            avg_likes = round(dct__['avg_likes'], 2)
            avg_comments = round(dct__['avg_comments'], 2)
            involvement = involvement_method(posts, blogger, months)  # вовлеченность
            coverage = round(coverage_method(posts), 2)
            cost = advertisement_price_method(posts, blogger)

            s = f"{blogger.login};{following};{len(posts)};{avg_likes};{avg_comments};{coverage};{cost};{involvement}"
            time_print(s)
            with open('bloggers_20k_26_02.csv', 'a', encoding='utf-8') as f:
                f.write(f'{s}\n')
        except Exception as e:
            print(blogger.login, '---', e)
            with open('error__bloggers_20k_26_02.csv','a',encoding='utf-8') as f:
                f.write(f'{blogger.login}\n')
