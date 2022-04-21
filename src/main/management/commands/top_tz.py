import typing
from collections import defaultdict
from datetime import datetime

from django.core.management import BaseCommand

# top_tz
# https://docs.google.com/spreadsheets/d/1SZ1B3LpsR_MhqkFuYmSCms7Ur7vE8RO4EqTIZLME0oY/edit?usp=sharing
from django.db.models import QuerySet, F

from main.models import Post, Blogger, Category
from rest.api.social.methods import posts_methods


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker1()


blogger_dct_er = {}


def posts_filter(posts: typing.Union[QuerySet[Post], typing.List[Post]]):
    #      01.03.2021 по 31.03.2022
    start = datetime.strptime('01.03.2021', '%d.%m.%Y').date()
    end = datetime.strptime('31.03.2022', '%d.%m.%Y').date()
    return posts.filter(date__range=(start, end))


def get_data_for_blg(blogger_login: str):
    blogger = Blogger.objects.get_default(login=blogger_login.replace('@', ''))
    start = datetime.strptime('01.03.2021', '%d.%m.%Y').date()
    end = datetime.strptime('31.03.2022', '%d.%m.%Y').date()
    posts = Post.objects.filter_default(blogger).filter(date__range=(start, end))

    likes = 0
    comments = 0
    for i in posts:
        likes += i.likes_count
        comments += i.comments_count

    er = (((likes + comments) / len(posts)) / blogger.default_total) * 100
    er = round(er, 2)
    likes_dt = round(likes / blogger.default_total, 2)
    comments_dt = round(comments / blogger.default_total, 2)

    return f'{blogger_login} (Охват: {er} ; Лайки/Кол-во подписчиков: {likes_dt} ; Комменты/Кол-во подписчиков: {comments_dt} )'


def get_advertisers(posts: typing.Union[QuerySet[Post], typing.List[Post]],
                    advertisers_and_blg_logins: dict,
                    blg_login: str):
    nicknames_all = []
    for post in posts:
        nicknames = posts_methods.last_advertiser_method_v2(post.text)
        nicknames_all.extend(list(nicknames.keys()))
    nicknames_all = set(nicknames_all)

    for nickname in nicknames_all:
        if nickname not in advertisers_and_blg_logins:
            advertisers_and_blg_logins[nickname] = []
        advertisers_and_blg_logins[nickname].append(f'@{blg_login}')


def get_top_from_advertisers(advertisers_and_blg_logins: dict):
    advertisers = advertisers_and_blg_logins.copy()
    advertisers = {k: v for k, v in sorted(advertisers.items(), key=lambda item: len(item[1]), reverse=True)}
    counter = 0
    ss = []
    for k, v in advertisers.items():
        ss.append(f'{k} (упоминающие профили: {len(v)}): {", ".join(v)}')
        # print(k, v)
        counter += 1
        if counter >= 10:
            break
    return ss


def get_top_from_advertisers2(advertisers_and_blg_logins: dict):
    advertisers = advertisers_and_blg_logins.copy()
    advertisers = {k: v for k, v in sorted(advertisers.items(), key=lambda item: len(item[1]), reverse=True)}
    counter = 0
    ss = []
    for k, v in advertisers.items():
        _s = "\n".join([get_data_for_blg(i) for i in v])
        ss.append(f'{k} (упоминающие профили: {len(v)}): \n{_s}')
        # print(k, v)
        counter += 1
        if counter >= 5:
            break
    return ss


def avg(num):
    sum_num = 0
    for t in num:
        sum_num = sum_num + t

    avg = sum_num / len(num)
    return round(avg, 2)


def worker1():
    # https://docs.google.com/document/d/1efGLlwe9SX4K1alP3nZzvdhN_-iK6WNI0b93Yi6NVWQ/edit
    countries = ['Англия', 'Франция', 'Германия', 'Испания']
    for country in countries:
        advertisers = dict()

        bloggers = Blogger.objects.filter(file_from_info__overlap=[country]) \
                       .order_by(F('default_total').desc(nulls_last=True))[:100]
        for blogger in bloggers:
            posts = Post.objects.filter_default(blogger)
            posts = posts_filter(posts)
            get_advertisers(posts, advertisers, blogger.login)
        results = get_top_from_advertisers(advertisers)
        b = '\n'.join(results)
        text = f"""Страна: {country}
ТОП-5 рекламодателей и профили из ТОП-100 блогеров {country}, в которых они упоминались:
{b}
        
        """
        with open('top_tz.csv', 'a', encoding='utf-8') as f:
            f.write(text)


def worker2():
    countries = ['Англия', 'Франция', 'Германия', 'Испания']
    for country in countries:
        advertisers = dict()

        bloggers = Blogger.objects.filter(file_from_info__overlap=[country]) \
                       .order_by(F('default_total').desc(nulls_last=True))[:100]
        for blogger in bloggers:
            posts = Post.objects.filter_default(blogger)
            posts = posts_filter(posts)
            get_advertisers(posts, advertisers, blogger.login)
        results = get_top_from_advertisers2(advertisers)
        b = '\n'.join(results)
        text = f"""Страна: {country}
ТОП-3 рекламодателей и профили из ТОП-100 блогеров {country}, в которых они упоминались:
{b}

            """
        with open('top_tz2.csv', 'a', encoding='utf-8') as f:
            f.write(text)


start = datetime.strptime('01.03.2021', '%d.%m.%Y').date()
end = datetime.strptime('31.03.2022', '%d.%m.%Y').date()


def worker3():
    countries = ['Англия', 'Франция', 'Германия', 'Испания']
    count = 0
    max_post = Post(likes_count=0, comments_count=0)
    for country in countries:
        bloggers = Blogger.objects.filter(file_from_info__overlap=[country])
        post = \
            Post.objects.filter(blogger_id__in=[i.id for i in bloggers], text__contains='@', date__range=(start, end)) \
                .order_by('-likes_count', '-comments_count')[:1][0]

        if (max_post.likes_count + max_post.comments_count) < (post.likes_count + post.comments_count):
            max_post = post

        print(country)
        print(f"@{post.blogger.login}")
        print(f'http://instagram.com/p/{post.post_id}/')

    print('Самый топовый')
    print(max_post.blogger.file_from_info[0])
    print(f'@{max_post.blogger.login}')
    print(f'http://instagram.com/p/{max_post.post_id}/')

    # count+=posts
    # print(count)


def worker4():
    countries = ['Англия', 'Франция', 'Германия', 'Испания']
    count = 0
    for country in countries:
        likes = 0
        comments = 0
        ers = []
        bloggers = Blogger.objects.filter(file_from_info__overlap=[country])
        for blogger in bloggers:
            posts = Post.objects.filter(blogger_id=blogger, date__range=(start, end)) \
                .order_by('-likes_count', '-comments_count')
            if len(posts) == 0:
                continue

            for i in posts:
                likes += i.likes_count
                comments += i.comments_count
            er = (((likes + comments) / len(posts)) / blogger.default_total) * 100
            er = round(er, 2)
            ers.append(er)

        print(country)
        print(likes, 'лайки')
        print(comments, 'комменты')
        print(avg(ers), 'средний er')


def worker7():
    countries = ['Англия', 'Франция', 'Германия', 'Испания']
    count = 0

    for country in countries:
        category_dct = defaultdict(int)
        bloggers = Blogger.objects.filter(file_from_info__overlap=[country]) \
                       .order_by(F('default_total').desc(nulls_last=True))[:100]
        for blogger in bloggers:
            category_dct[blogger.category_id] += 1
        data = {k: v for k, v in sorted(category_dct.items(), key=lambda item: item[1], reverse=True)}
        print(f'{country} ТОП-3 повторяющихся категорий')
        counter = 0
        for key, value in data.items():
            if key is None or key == 4:
                continue

            print('Категория:', f'"{Category.objects.get(id=key).name}"', 'Количество:', value)
            counter += 1
            if counter == 5:
                break
        print()


def worker7_1():
    countries = ['Англия', 'Франция', 'Германия', 'Испания']
    count = 0
    category_dct = defaultdict(int)
    bloggers = list(Blogger.objects.filter(file_from_info__overlap=countries).values_list('social_id', flat=True))
    with open('bloggers_top.csv', 'w') as f:
        f.write('\n'.join(bloggers))


def worker8():
    countries = ['Англия', 'Франция', 'Германия', 'Испания']

    for country in countries:
        hashtags_dct = {}

        bloggers = Blogger.objects.filter(file_from_info__overlap=[country]) \
                       .order_by(F('default_total').desc(nulls_last=True))[:100]
        for blogger in bloggers:
            posts = Post.objects.filter(blogger=blogger, date__range=(start, end)).only('id', 'text')
            for post in posts:
                posts_methods.tags_method(post.text, hashtags_dct)
        data = {k: v for k, v in sorted(hashtags_dct.items(), key=lambda item: item[1], reverse=True)}
        counter = 0
        print(country)
        for key, value in data.items():
            print('Тэг:', f'"{key}"', 'Количество:', value)
            counter += 1
            if counter == 10:
                break
