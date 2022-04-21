# util
import json
import os
import random
import time
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

import requests
from django.core.management import BaseCommand
from django.db.models import Q, F, Sum, Case, When

from api.serializers import GlobalTopSerializer
from flood.models import ParsingTaskBloggerStatus, ParsingTaskMicroservice
from intercalation.management.commands.tasks_progress import get_data
from intercalation.work_modules.TaskCreator import TaskCreator
from main.models import Blogger, Post, Subscriber, Address, Comment
from parsing.AsyncParsingNew.utils import time_print, chunks
from parsing.management.commands.translator import Translate
from rest.api.social.methods import util_methods, posts_methods
from rest.api.social.methods.posts_methods import advertisement_price_method
from rest.api.top.general import metrics


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        worker()


def check_word(word: str):
    alf = list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    for i in word:
        if i in alf:
            return True
    return False


def post_to_dict(post: Post):
    photo_url = util_methods.create_photo_link(post.photos_url)
    post.text = post.text.replace('\n', ' ')
    return {'post_id': post.post_id,
            'post_login': post.post_login,
            'post_url': f"https://www.instagram.com/p/{post.post_id}/",
            'photos_url': [photo_url],
            'text': post.text,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'time': post.date.strftime('%H:%M'),
            'date': post.date.strftime('%Y-%m-%d'),
            }


def comment_to_dict(comment: Comment, social_id, post_id):
    #     {"blogger_social_id": "1037140901", "post_id": "CLBZm19hZw3", "text": "Все классные!!!", "comment_id": "17971368184401343", "commentator_social_id": "5921539240", "commentator_login": "zaeaulea"}
    return {
        "blogger_social_id": social_id,
        "post_id": post_id,
        "text": comment.text,
        "comment_id": comment.comment_id,
        "commentator_social_id": comment.commentator_social_id,
        "commentator_login": comment.commentator_login
    }


def worker():
    ids = list(Blogger.objects.filter(login__in=['karna.val', 'navalny']).values_list('id', flat=True))

    d=Blogger.objects.filter(id__in=ids).annotate(
        likes_count=Sum(Case(When(posts__is_deleted=False, then=F('posts__likes_count')))))
    for i in d:
        print(i.login,i.likes_count)

    return
    # bloggers = Blogger.objects.filter(file_from_info__overlap=['Инстаграм боты2'])
    # counter = 0
    # size = len(bloggers)
    # for blogger in bloggers:
    #     t, c = TaskCreator.create_parsing_task(blogger)
    #     posts = Post.objects.filter_default(blogger=blogger)
    #     TaskCreator.comments(t, posts, limit=100)
    #
    # return
    #
    # with open(r'C:\Users\Marat\Documents\GitHub\python_github\potok\HypeProject\bots2.txt', 'r', encoding='utf-8') as f:
    #     data = f.read().strip().split('\n')
    # blgs = []
    # bloggers = Blogger.objects.filter(login__in=data, social_network_type_id=3).values_list('login', flat=True)
    # bloggers = list(bloggers)
    # for i in bloggers:
    #     data.remove(i)
    # with open(r'C:\Users\Marat\Documents\GitHub\python_github\potok\HypeProject\bots3.txt', 'w', encoding='utf-8') as f:
    #     f.write('\n'.join(data))
    #
    # return
    # bloggers = Blogger.objects.filter(file_from_info__overlap=['Инстаграм боты2'])
    # counter = 0
    # size = len(bloggers)
    # for blogger in bloggers:
    #     t, c = TaskCreator.create_parsing_task(blogger)
    #     posts = Post.objects.filter_default(blogger)[:20]
    #     TaskCreator.comments(t, posts, limit=500)
    #     print(counter, size)
    #     counter += 1
    #
    # return
    # countries = ['Англия', 'Франция', 'Германия', 'Испания']
    #
    # for country in countries:
    #     bloggers = Blogger.objects.filter(file_from_info__overlap=[country]) \
    #                    .order_by(F('default_total').desc(nulls_last=True))[:100]
    #     for blogger in bloggers:
    #         t, c = TaskCreator.create_parsing_task(blogger)
    #         TaskCreator.subscriber_not_detail(t, limit=500_000)
    #
    # return
    # last_id = 0
    # size = 27654757
    # max_id = 591633868
    # print('size', size)  # 27654757
    # print('max id', max_id)  # 591633868
    # counter = 0
    # while True:
    #     subscribers = list(
    #         Subscriber.objects.filter(status_id=2, id__gt=last_id).order_by('id')[:50_000].only('id', 'status_id'))
    #     counter += len(subscribers)
    #
    #     if len(subscribers):
    #         last_id = subscribers[-1].id
    #     else:
    #         break
    #
    #     for s in subscribers:
    #         s.status_id = 1
    #
    #     Subscriber.objects.bulk_update(subscribers, fields=['status_id'])
    #     time_print('last id', last_id, "counter", counter, 'of', size)
    #
    #     if last_id > max_id:
    #         break
    #
    # return
    # blgs = Blogger.objects.filter(file_from_info__overlap=['Франция'])
    # for blg in blgs:
    #     t, c = TaskCreator.create_parsing_task(blg)
    #     TaskCreator.posts(t)
    #
    # return
    # with open(r'C:\Users\Marat\Documents\GitHub\python_github\potok\HypeProject\france_top_ids.txt', 'r') as f:
    #     d = f.read().strip().split('\n')
    # blgs = Blogger.objects.filter(social_network_type_id=3, social_id__in=d)
    # for i in blgs:
    #     i.file_from_info = ['Франция']
    # Blogger.objects.bulk_update(blgs, fields=['file_from_info'])
    #
    # return
    # countries = ['Вьетнам', 'Италия', 'Польша']
    # for country in countries:
    #     bloggers = Blogger.objects.filter(social_network_type_id=3, file_from_info__overlap=[country]).order_by(
    #         F('default_total').desc(nulls_last=True))[:10]
    #     print(country)
    #     for i in bloggers:
    #         print(i.login)
    #     print()
    #
    # return
    # posts = Post.objects.filter(photos_url__startswith='http').count()
    #
    # return
    # blg = Blogger.objects.get_default(login='zidane')
    # for post in list(Post.objects.filter_default(blogger=blg).values_list('id', flat=True)):
    #     comments = Comment.objects.filter(post_id=post).only('id', 'is_done')
    #     for c in comments:
    #         c.is_done = False
    #     Comment.objects.bulk_update(comments, fields=['is_done'])
    #     print(len(comments))
    # return
    #
    # bloggers = Blogger.objects.filter(file_from_info__overlap=['Топ'])
    # counter = 0
    # size = len(bloggers)
    # for blg in bloggers:
    #     posts = Post.objects.filter_default(blogger=blg)
    #     try:
    #         brands = posts_methods.brand_affinity(posts, 'ru')
    #         brands = list(brands.keys())
    #         blg.advertisers_ids = brands
    #     except:
    #         brands = []
    #         pass
    #     try:
    #         er = float(blg.create_er())
    #         blg.engagement_rate = Decimal(str(er))
    #     except:
    #         er = 0.0
    #         pass
    #
    #     blg.save(update_fields=['advertisers_ids', 'engagement_rate'])
    #     time_print(counter, 'of', size, 'advertisers', brands, 'er', er)
    #     counter += 1
    #
    # return
    # countries = ["Испания", "Индонезия", "Польша", "Италия", "Вьетнам", "Узбекистан",
    #              "Азербайджан", "Германия", "Португалия", "Тайланд", "Англия", 'Россия']
    # c = 0
    # for country in countries:
    #     blgs = Blogger.objects.filter(file_from_info__overlap=[country]).order_by(
    #         F('default_total').desc(nulls_last=True))[:50]
    #     for i in blgs:
    #         if 'Топ' not in i.file_from_info:
    #             i.file_from_info.append('Топ')
    #     Blogger.objects.bulk_update(blgs, fields=['file_from_info'])
    #
    #     print(country, len(blgs))
    #     c += len(blgs)
    # print(c)
    # return
    #
    # while True:
    #     blgs = Blogger.objects.filter(file_from_info__overlap=countries).only('id', 'file_from_info')[:10_000]
    #     for i in blgs:
    #         i.file_from_info.remove('Россия 18+')
    #         i.file_from_info.append('Россия')
    #     Blogger.objects.bulk_update(blgs, fields=['file_from_info'])
    #     print(len(blgs))
    #     if len(blgs) == 0:
    #         break
    #
    # return
    #
    # metrics.metrics()
    # return
    # a = GlobalTopSerializer(Blogger.objects.first())
    # print(a.data)
    #
    # return
    # tasks = ParsingTaskMicroservice.objects.filter(status=ParsingTaskBloggerStatus.not_started).count()
    # print(tasks)
    # return

    blgs = Blogger.objects.filter(file_from_info__overlap=['Инстаграм боты2']).values_list('social_id', flat=True)
    for i in blgs:
        print(i)

    return

    try:
        os.mkdir('bots_business')
    except:
        pass
    path1 = os.path.join('bots_business', 'users')
    try:
        os.mkdir(path1)
    except:
        pass

    path2 = os.path.join('bots_business', 'comments')

    try:
        os.mkdir(path2)
    except:
        pass

    with open(os.path.join(path1, 'users.csv'), 'r', encoding='utf-8') as f:
        data = f.read().strip().split('\n')

    dct = {}
    counter = 0
    size = len(data)
    for line in data:
        a, b = line.split(':', maxsplit=1)
        temp_data = json.loads(b)
        social_id = str(temp_data['user']['pk'])
        blogger = Blogger.objects.get(social_id=social_id, social_network_type_id=3)

        blogger.bio = str(blogger.bio).replace('\n', ' ').replace('None', '')
        posts = Post.objects.filter(blogger_id=blogger.id)
        posts_arr = [post_to_dict(post) for post in posts]
        temp_data['posts'] = posts_arr
        q = f'{json.dumps(temp_data, ensure_ascii=False)}\n'
        comments = Comment.objects.filter(post_id__in=[i.id for i in posts])
        comments_arr = []
        for c in comments:
            c.text = c.text.replace('\n', ' ')
            c_t = comment_to_dict(c, social_id, c.post_id)
            t = f'{json.dumps(c_t, ensure_ascii=False)}\n'

            comments_arr.append(t)

        with open(os.path.join(path2, 'comments.csv'), 'a', encoding='utf-8') as f:
            f.write(''.join(comments_arr))

        with open(os.path.join(path1, 'users_output.csv'), 'a', encoding='utf-8') as f:
            f.write(''.join(q))

        time_print('c', counter, 's', size)
        counter += 1
    # bloggers = Blogger.objects.filter(file_from_info__overlap=['Инстаграм боты'])
    # for i in bloggers:
    #     print(i.social_id)

    return
    # tasks = ParsingTaskMicroservice.objects.filter(status=ParsingTaskBloggerStatus.not_started).count()
    # print(tasks)
    #
    # return
    time.sleep(60 * 60)
    bloggers = Blogger.objects.filter(file_from_info__overlap=['Инстаграм боты'])
    counter = 0
    size = len(bloggers)
    for blogger in bloggers:
        t, c = TaskCreator.create_parsing_task(blogger)
        posts = Post.objects.filter_default(blogger)[:20]
        TaskCreator.comments(t, posts, limit=500)
        print(counter, size)
        counter += 1

    return
    last_id = 0
    counter = 0
    countries = ["Russia", "Россия", "РФ", "Российская федерация"]
    addresses = list(Address.objects.filter(native_country__in=countries).values_list('city_id', flat=True))

    while True:

        q = ((Q(id__gt=last_id) & Q(avatar__isnull=False) & Q(social_network_type_id=3)) & (
                Q(address_id__in=addresses) | ~Q(bio=None)))
        subs = Subscriber.objects.filter(q).order_by('id').only("id", "login", "social_id", "avatar", 'bio')[:100_000]
        subs_list = list(filter(lambda x: check_word(x.bio), list(subs)))

        counter += len(subs_list)
        index = counter // 10_000_000
        arr = [f'{sub.login};{sub.social_id};{sub.avatar}\n' for sub in subs_list]

        try:
            last_id = subs_list[-1].id
        except Exception as e:
            print(e)

        time_print("subs len", len(arr), "index of file", index, "counter", counter)

        with open(f"subscribers_avatars_rus_{index}_apr.csv", 'a', encoding='utf-8') as f:
            f.write(''.join(arr))

    return
    # 25142
    t, c = TaskCreator.create_parsing_task(None)
    a = TaskCreator.filtering_bloggers(t, ["renat_f14", "kamilyaxa", "ilnur1312"])
    print(a)

    return
    s = Subscriber.objects.filter(~Q(avatar=None)).count()
    print(s)

    return
    last_id = 0
    counter = 0
    while True:

        subscribers = Subscriber.objects.filter(Q(id__gt=last_id) & ~Q(avatar=None) & Q(social_network_type_id=3)) \
                          .only('id', 'login', 'social_id', 'avatar')[:100_000]
        subscribers = list(subscribers)
        counter += len(subscribers)

        index = counter // 10_000_000
        arr = []
        for sub in subscribers:
            s = f'{sub.login};{sub.social_id};{sub.avatar}\n'
            arr.append(s)

        try:
            last_id = subscribers[-1].id
        except Exception as e:
            print(e)
            break

        time_print('subs len', len(arr), 'index of file', index, 'counter', counter)
        with open(f'subscribers_avatars_{index}_.csv', 'a', encoding='utf-8') as f:
            f.write(''.join(arr))

    return
    bloggers = Blogger.objects.filter(file_from_info__overlap=['Италия'], id=2124589).values_list('id', flat=True)
    bloggers = list(bloggers)

    s = Subscriber.objects.filter(bloggers__overlap=bloggers[:100]).count()
    print(s)

    a = Comment.objects.filter(is_done=False).count()
    print(a)

    return
    a = ParsingTaskMicroservice.objects.filter(status=ParsingTaskBloggerStatus.in_process, parser_task_id=None).update(
        status=ParsingTaskBloggerStatus.not_started)

    return
    bloggers = Blogger.objects.filter(file_from_info__overlap=['Польша'])
    for blogger in bloggers:
        t, c = TaskCreator.create_parsing_task(blogger)
        posts = Post.objects.filter_default(blogger)
        date_min = datetime.strptime('09:2021', '%m:%Y')
        dct = {}
        for p in posts:
            if p.date > date_min:
                dct[p.date_str] = p

        print(len(posts))
        print(len(dct.values()))

        TaskCreator.comments(t, list(dct.values()))
        TaskCreator.likes(t, list(dct.values()))

    return
    a = Subscriber.objects.filter(followers=None).count()
    print(a)

    return
    bloggers = Blogger.objects.filter(file_from_info__overlap=['Польша'])
    for blogger in bloggers:
        t, c = TaskCreator.create_parsing_task(blogger)
        TaskCreator.subscriber_not_detail(t)

    # t, c = TaskCreator.create_parsing_task(None)
    # TaskCreator.filtering_bloggers(t, [i.social_id for i in bloggers])

    return
    counter = 0
    bloggers = Blogger.objects.filter(social_network_type_id=3).order_by(F('default_total').desc(nulls_last=True)).only(
        'id', 'login', 'default_total')
    size = len(bloggers)
    for blogger in bloggers:
        try:
            posts = Post.objects.filter_default(blogger).only('id', 'comments_count', 'comments_count')
            cost = advertisement_price_method(posts, blogger)
            with open('advertisement_price.csv', 'a', encoding='utf-8') as f:
                f.write(f'{blogger.login};{cost}\n')
        except Exception as e:
            print(e)
        counter += 1
        print(counter, 'of', size)

    #
    #
    #
    #     return
    #     with open('without_comments_all_new', 'r', encoding='utf-8') as f:
    #         data = f.read().strip().split('\n')
    #

    #
    #     for i in data:
    #         dct = {}
    #         blogger = Blogger.objects.get(id=int(i))
    #         posts = Post.objects.filter_default(blogger)
    #         for p in posts:
    #             if p.date > date_min:
    #                 dct[p.date_str] = p
    #         t, c = TaskCreator.create_parsing_task(blogger)
    #         TaskCreator.comments(t, list(dct.values()),limit=100)
    #     return
    #
    #     from django.db import models
    #
    #     class ArrayLength(models.Func):
    #         function = 'CARDINALITY'
    #
    #     blgs = Blogger.objects.filter(social_network_type_id=3).only('id')
    #     size = len(blgs)
    #     print(size)
    #     counter = 0
    #     for blg in blgs:
    #         posts = list(Post.objects.filter_default(blg).values_list('id', flat=True))
    #         comments = Comment.objects.filter(post_id__in=posts).exists()
    #         if not comments:
    #             with open('without_comments_all_new', 'a', encoding='utf-8') as f:
    #                 f.write(f'{blg.id}\n')
    #
    #         print(counter, 'of', size)
    #         counter += 1
    #
    #     # for blg in Blogger.objects.filter(social_network_type_id=3, login__in=['ulugbekhon', 'justking31']):
    #     #     t, c = TaskCreator.create_parsing_task(blg)
    #     #     TaskCreator.posts(t)
    #     #     TaskCreator.subscribers(t, limit=100)
    #     #     TaskCreator.comments(t, Post.objects.filter_default(blg), limit=200)
    # #
    # #
    # # aaa = """a4omg
    # # _agentgirl_
    # # annymay
    # # borodylia
    # # buzova86
    # # dava_m
    # # egorkreed
    # # gggboxing
    # # gusein.gasanov
    # # justking31
    # # kair_n
    # # karna.val
    # # khabib_nurmagomedov
    # # litvinchannel
    # # navalny
    # # pavelvolyaofficial
    # # samoylovaoxana
    # # sekavines
    # # sheidlina
    # # timatiofficial
    # # ulugbekhon
    # # zidane""".strip().split('\n')
    # #     for i in aaa:
    # #         blg = Blogger.objects.get_default(login=i)
    # #         posts = list(Post.objects.filter_default(blg).values_list('id', flat=True))
    # #         comments = Comment.objects.filter(post_id__in=posts).exists()
    # #         print(blg.login, comments)
    # #
    # #     return
    # # with open(r'C:\Users\Marat\Documents\GitHub\python_github\potok\HypeProject\src\social_id__address.csv') as f:
    # #     data=f.read().strip().split('\n')
    # # s=[]
    # # for i in data:
    # #     s.append(i.split(';')[0])
    # # with open('socials.csv','w') as f:
    # #     f.write('\n'.join(s))
    # # return
    # # #
    # # #
    # # # return
    # # # counter = 0
    # # # addresses = Address.objects.all()
    # # # tr = Translate()
    # # # for i in addresses:
    # # #     i:Address
    # # #     if not check_word(i.native_city):
    # # #         tr.translate([i.native_city],'ru')
    # # #
    # # # return
    # # # size = len(addresses)
    # # counter = 0
    # # addresses = Address.objects.filter(latitude_longitude=None)
    # # size = len(addresses)
    # # for address in addresses:
    # #     try:
    # #         subs = list(Subscriber.objects.filter(address_id=address.city_id).values_list('social_id',flat=True))
    # #             sub = subs[0]
    # #             with open('social_id__address.csv', 'a', encoding='utf-8') as f:
    # #                 f.write(f'{sub.social_id};{address.city_id}\n')
    # #             print(f'{sub.social_id};{address.city_id}')
    # #         else:
    # #             blgs = list(Blogger.objects.filter(address_id=address.city_id).values_list('social_id',flat=True))
    # #             sub = random.choice(blgs)
    # #             with open('social_id__address.csv', 'a', encoding='utf-8') as f:
    # #                 f.write(f'{sub};{address.city_id}\n')
    # #             print(f'{sub};{address.city_id}')
    # #
    # #         print('counter', counter, 'of', size)
    # #         counter += 1
    # #     except Exception as e:
    # #         with open('error_data_address.csv', 'a', encoding='utf-8') as f:
    # #             f.write(f'{address.city_id}\n')
    # #
    # # return
    # # with open(r'top_100.csv', 'r') as f:
    # #     data = f.read().strip().split('\n')
    # #
    # # blgs = Blogger.objects.filter(social_network_type_id=3, login__in=data).order_by('id').values_list('id', flat=True)
    # # blgs = list(blgs)
    # # index = 0
    # # counter = 0
    # # last_id = 0
    # # while True:
    # #     subs = list(Subscriber.objects.filter(bloggers__overlap=blgs, id__gt=last_id)[:10_000])
    # #     s = []
    # #     for sub in subs:
    # #         age = age_func(sub.age)
    # #         gender = gender_func(sub)
    # #         address = address_func(sub.address_id)
    # #         l = f"{sub.social_id},{gender},{age},,,{address},\n"
    # #         s.append(l)
    # #
    # #     index += 1
    # #     counter += len(s)
    # #     last_id = subs[-1].id
    # #
    # #     with open('output_rf18_top_100.csv', 'a', encoding='utf-8') as f:
    # #         f.write(''.join(s))
    # #     print(len(s), 'len s', 'counter', counter, 'index', index)
    # #
    # # return
    # #
    # # a = Blogger.objects.select_related('address').filter(
    # #     ~Q(file_from_info__overlap=['Россия 18+']) & ~Q(address_id=None)).values_list('id', flat=True)
    # # s = list(a)
    # # print('blgs', len(s))
    # # counter = 0
    # # index = 0
    # # data = set()
    # #
    # # for mini in chunks(s, 100):
    # #     subs = list(Subscriber.objects.filter(bloggers__overlap=mini).values_list('id', flat=True))
    # #     print('subs', len(subs))
    # #     data = data | set(list(map(str, subs)))
    # #
    # #     print('data', len(data))
    # #     index += 1
    # #     print('index', index)
    # #
    # # with open('ids_subs_unique.csv', 'w') as f:
    # #     f.write('\n'.join(list(data)))
    # #
    # # # 27.965.933
    # # return
    # # a = Address.objects.filter(Q(city_name__icontains='россия') | Q(native_city__icontains='россия') | Q(
    # #     native_country__icontains='россия')).count()
    # # print(a)
    # # return
    # #
    # # a = Subscriber.objects.filter(~Q(address_id=None)).count()
    # # print(a)
    # #
    # # return
    # # q = Q(status=ParsingTaskBloggerStatus.in_process)
    # # tasks = list(ParsingTaskMicroservice.objects.filter(q).only('id', 'parser_task_id', 'progress'))
    # # for mini_tasks in chunks(tasks, 1000):
    # #     dct = {}
    # #     for i in mini_tasks:
    # #         i: ParsingTaskMicroservice
    # #         dct[str(i.parser_task_id)] = i
    # #     print(dct)
    # #     data = get_data(list(dct)).get('data')
    # #     arr = []
    # #     for k in dct:
    # #         if k in data:
    # #             progress = data[k]
    # #             obj = dct[k]
    # #             obj.progress = progress
    # #             arr.append(obj)
    # #     ParsingTaskMicroservice.objects.bulk_update(arr, fields=['progress'])
    # #     time_print('updated', len(arr))
    # #
    # # return
    # # blg = Blogger.objects.get_default(login='navalny')
    # # t, c = TaskCreator.create_parsing_task(blg)
    # # TaskCreator.posts(t)
    # # TaskCreator.subscribers(t, limit=100)
    # # TaskCreator.comments(t, Post.objects.filter_default(blg)[:10])
    # # TaskCreator.likes(t, Post.objects.filter_default(blg)[:10])
    # # TaskCreator.filtering_bloggers(t, [blg.social_id])
    # # TaskCreator.subscriber_not_detail(t, limit=100)
