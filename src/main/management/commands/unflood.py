import time

from django.core.management import BaseCommand

# unflood
from django.db import connection
from django.db.models import Count

from main.models import Blogger, Subscriber


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def worker():
    st = time.monotonic()
    t = Subscriber.objects.filter_with_timeout([16157],5)[:5]
    print(time.monotonic()-st)
    print(t)


    return
    with open('unflood.csv', 'r') as f:
        data = f.read().strip().replace(' ', '').split('\n')
    dct = {}
    a=Blogger.objects.filter(login__in=data)
    c=0
    for i in a:
        i.delete()
        c+=1
        print(c,len(a))
    print(a)


    return
    for i in data:
        social_id, login, followers, following, posts_count = i.split(':')
        following = int(following)
        followers = int(followers)
        posts_count = int(posts_count)
        dct[login] = (social_id, login, followers, following, posts_count)

    bloggers = Blogger.objects.filter(login__in=list(dct.keys()))
    for blogger in bloggers:
        social_id, login, followers, following, posts_count = dct[blogger.login]
        blogger.social_id = social_id
        blogger.default_total = followers
        blogger.following = following
        blogger.post_default_count = posts_count
    Blogger.objects.bulk_update(list(bloggers),
                                fields=['social_id', 'default_total', 'following', 'post_default_count'],
                                batch_size=5_000)
    print('done',len(bloggers))
