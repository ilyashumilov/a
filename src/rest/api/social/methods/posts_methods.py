import datetime
from typing import List

from django.db.models import QuerySet

from api.services.brands_from_text import get_brand
from brand_parser.models import Brand
from main.models import Post, Blogger
from rest.api.social.methods import util_methods, serializer_methods
from rest.api.social.methods.text_methods import create_steps, capwords, \
    check_word_exclude, last_advertiser_method_v2, tags_method
from rest.api.social.methods.util_methods import round_
from rest.api.social.services import blogger_service
from rest.api.social.services.language_controller import LanguageController


def involvement_engagement_rate_method(posts: QuerySet[Post], blogger: Blogger, dct: dict, months: list):
    global_er = dict(likes=0, comments=0)
    global_counter = 0
    limit = 12

    for post in posts:

        if global_counter < limit:
            global_er['likes'] += post.likes_count
            global_er['comments'] += post.comments_count
            global_counter += 1

        if months[0] not in dct:
            for month in months:
                dct[month] = {
                    'date': post.date,
                    'posts_count': 0,
                    'likes': 0,
                    'comments': 0
                }

        t_date = post.date_str
        if t_date not in months:
            continue

        t = dct[t_date]
        t['posts_count'] += 1
        t['likes'] += post.likes_count
        t['comments'] += post.comments_count

    avg_er = 0
    for key, value in dct.items():
        er = util_methods.calculate_er(value['likes'], value['comments'], blogger)
        avg_er += er

        posts_count = value['posts_count'] if value['posts_count'] > 0 else 1

        value['avg_likes'] = round_(util_methods.divide(value['likes'], posts_count), 1)
        value['avg_comments'] = round_(util_methods.divide(value['comments'], posts_count), 1)
        value['er'] = round_(avg_er, 2)
        del value['date']

    dct['avg_er'] = round_(util_methods.divide(avg_er, (len(dct) - 2)), 0)

    last_not_zero_month = 1
    for i in months[::-1]:
        try:
            if dct[i]['er'] > 0:
                last_not_zero_month = dct[i]['er']
                break
        except:
            pass

    dct['percent'] = round_(util_methods.calculate_percent(dct[months[0]]['er'], last_not_zero_month), 0)

    dct['global_avg_er'] = round_(
        util_methods.calculate_er(global_er['likes'], global_er['comments'], blogger, global_counter), 0)
    dct['global_percent'] = round_(util_methods.calculate_percent(dct['global_avg_er'], last_not_zero_month), 0)

    return dct


def posts_months_method(posts: QuerySet[Post], dct: dict):
    posts = list(posts)
    months = util_methods.get_months_between_two_post(posts[0], posts[-1])
    for month in months:
        dct[month] = {
            "posts": 0,
            "advertising_posts": 0
        }

    for post in posts:
        dct['__likes'] += post.likes_count
        dct['__comments'] += post.comments_count

        t_date = post.date_str

        if len(last_advertiser_method_v2(post.text)):
            dct[t_date]['advertising_posts'] += 1
        else:
            dct[t_date]['posts'] += 1


def comments_by_post_method(posts: QuerySet[Post], dct: dict, months: list):
    global_avg_comments = 0
    global_posts_count = len(posts)
    global_percent = dict(min_date=datetime.datetime.now(), posts_count=0, comments=0)

    for month in months:
        dct[month] = {
            'comments': 0,
            'posts_count': 0,
            'avg_comments': 0
        }

    dct['avg_comments'] = 0
    dct['count'] = 0
    for post in posts:
        global_avg_comments += post.comments_count

        t_datetime = datetime.datetime.strptime(post.date_str, '%m.%Y')

        if t_datetime < global_percent['min_date']:
            global_percent['min_date'] = t_datetime
            global_percent['posts_count'] = 1
            global_percent['comments'] = post.comments_count
        elif t_datetime == global_percent['min_date']:
            global_percent['posts_count'] += 1
            global_percent['comments'] += post.comments_count

        t_date = post.date_str

        if t_date not in months:
            continue

        t = dct[t_date]
        t['comments'] += post.comments_count
        t['posts_count'] += 1
        t['avg_comments'] = util_methods.round_(util_methods.divide(t['comments'], t['posts_count']), 1)

        dct['avg_comments'] += post.comments_count

        dct['count'] += 1

    dct['avg_comments'] = round_(util_methods.divide(dct.get('avg_comments', 1), dct.get('count', 1)), 1)

    last_not_zero_month = 1
    for i in months[::-1]:
        if dct[i]['avg_comments'] > 0:
            last_not_zero_month = dct[i]['avg_comments']
            break
    dct['percent'] = util_methods.calculate_percent(dct[months[0]]['avg_comments'], last_not_zero_month)
    dct['global_avg_comments'] = round_(util_methods.divide(global_avg_comments, global_posts_count), 1)

    global_avg_comments_first_month = util_methods.divide(global_percent['comments'], global_percent['posts_count'])
    dct['global_percent'] = util_methods.calculate_percent(global_avg_comments_first_month, last_not_zero_month)


def likes_by_post_method(posts: QuerySet[Post], dct: dict, months: list):
    global_avg_likes = 0
    global_posts_count = len(posts)
    global_percent = dict(min_date=datetime.datetime.now(), posts_count=0, likes=0)

    for month in months:
        dct[month] = {
            'likes': 0,
            'posts_count': 0,
            'avg_likes': 0
        }
    dct['avg_likes'] = 0
    dct['count'] = 0

    for post in posts:
        global_avg_likes += post.likes_count

        t_datetime = datetime.datetime.strptime(post.date_str, '%m.%Y')

        if t_datetime < global_percent['min_date']:
            global_percent['min_date'] = t_datetime
            global_percent['posts_count'] = 1
            global_percent['likes'] = post.likes_count
        elif t_datetime == global_percent['min_date']:
            global_percent['posts_count'] += 1
            global_percent['likes'] += post.likes_count

        t_date = post.date_str
        if t_date not in months:
            continue

        t = dct[t_date]
        t['likes'] += post.likes_count
        t['posts_count'] += 1
        t['avg_likes'] = round_(util_methods.divide(t['likes'], t['posts_count']), 1)

        dct['avg_likes'] += post.likes_count

        dct['count'] += 1

    dct['avg_likes'] = round_(util_methods.divide(dct['avg_likes'], dct['count']), 1)

    last_not_zero_month = 1
    for i in months[::-1]:
        if dct[i]['avg_likes'] > 0:
            last_not_zero_month = dct[i]['avg_likes']
            break

    dct['percent'] = util_methods.calculate_percent(dct[months[0]]['avg_likes'], last_not_zero_month)
    dct['global_avg_likes'] = round_(util_methods.divide(global_avg_likes, global_posts_count), 1)

    global_avg_likes_first_month = util_methods.divide(global_percent['likes'], global_percent['posts_count'])
    dct['global_percent'] = util_methods.calculate_percent(global_avg_likes_first_month, last_not_zero_month)


def best_time_to_publish_method(posts: QuerySet[Post], dct: dict, blogger: Blogger):
    posts_count = 0
    likes_count = 0
    comments_count = 0
    for post in posts:
        posts_count += 1
        likes_count += 1
        comments_count += 1

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
        t['er'] = util_methods.calculate_er(t['likes_comments'], 0, blogger, t['posts_count'])

    dct['work_data'] = {
        "max_posts": 0,
        "max_likes": 0,
        "max_comments": 0,
        "max_er": 0
    }
    work_keys = list(dct['work_data'].keys())

    def best_comparison_max(dct__: dict, name__, value__):
        if dct__['work_data'][name__] < value__:
            dct__['work_data'][name__] = value__

    for i, v in dct.items():
        if i == 'work_data':
            continue
        coeff_posts = util_methods.divide(v['posts_count'], posts_count)
        coeff_likes = util_methods.divide(v['likes'], likes_count)
        coeff_comments = util_methods.divide(v['comments'], comments_count)
        coeff_er = util_methods.divide(v['er'], blogger.er)

        best_comparison_max(dct, 'max_posts', coeff_posts)
        best_comparison_max(dct, 'max_likes', coeff_likes)
        best_comparison_max(dct, 'max_comments', coeff_comments)
        best_comparison_max(dct, 'max_er', coeff_er)

    create_steps(dct['work_data'].keys(), dct, 7)

    for i, v in dct.items():
        if i == 'work_data':
            continue
        coeff_posts = util_methods.divide(v['posts_count'], posts_count)
        coeff_likes = util_methods.divide(v['likes'], likes_count)
        coeff_comments = util_methods.divide(v['comments'], comments_count)
        coeff_er = util_methods.divide(v['er'], float(blogger.engagement_rate))

        coeffs = dict(max_posts=coeff_posts, max_likes=coeff_likes, max_comments=coeff_comments, max_er=coeff_er)

        for key in work_keys:
            right_key = key.split('_')[1]
            steps = dct['work_data'][f'{key}__steps']

            for step_index in range(len(steps) - 1):
                if steps[step_index] < coeffs[key] <= steps[step_index + 1]:
                    dct[i][f'{right_key}_step'] = step_index + 1
                    break
    return dct


def tags_in_posts_method(posts: QuerySet[Post], dct: dict):
    for post in posts:
        tags_method(post.text.lower(), dct)


def the_most_popular_posts(posts: QuerySet[Post], array: list):
    posts = posts.filter(text__contains='@').order_by('-likes_count', '-comments_count')[:3]

    for post in posts:
        array.append(serializer_methods.post_to_dict(post))


def last_advertisers(posts: QuerySet[Post], blogger: Blogger, language):
    dct = {}
    new_dct = {}
    arr = []
    for post in posts:
        t_dct = last_advertiser_method_v2(post.text)
        for n in t_dct.keys():
            if n == blogger.login:
                continue
            dct[n] = {'login': capwords(str(n)), 'photo': None, 'category': ""}
            arr.append(n)
    t_blgs = Blogger.objects.select_related('category').prefetch_related(
        util_methods.posts_prefetch_control()).select_related('status') \
        .filter(social_network_type_id=3, login__in=arr)
    advertisers_dct = {}
    for i in t_blgs:
        advertisers_dct[i.login] = i
    for i in arr:
        try:
            advertiser = advertisers_dct[i]
            if advertiser.login == blogger.login:
                continue

            new_dct[advertiser.login] = blogger_service.blogger_profile(advertiser, language)
        except:
            pass

    return new_dct


def brand_affinity(posts: QuerySet[Post], language: str):
    unique_words = set()
    for post in posts:
        for word in set(post.text.split()):
            if not check_word_exclude(word):
                unique_words.add(word)
    dct = {}
    try:
        for i in unique_words:
            i = str(i).lower()
            if not check_word_exclude(i):
                t = get_brand(i)
                if t is not None:
                    if not check_word_exclude(t['name']):
                        dct[t['id']] = t

    except:
        pass

    brands = Brand.objects.filter(id__in=list(dct.keys()))
    new_dct = {}
    for brand in brands:
        try:
            url = str(brand.img)
        except:
            url = None

        new_dct[brand.id] = {
            "id": brand.id,
            "name": brand.name,
            "photo": url
        }

    return new_dct


def metrics_method(posts: QuerySet[Post], blogger):
    avg_likes = 0
    avg_comments = 0
    for post in posts:
        avg_likes += post.likes_count
        avg_comments += post.comments_count
    likes = avg_likes
    comments = avg_comments
    avg_likes = util_methods.divide(avg_likes, len(posts))
    avg_comments = util_methods.divide(avg_comments, len(posts))

    return dict(avg_likes=avg_likes, avg_comments=avg_comments, likes_count=likes, comments_count=comments)


def involvement_method(posts: QuerySet[Post], blogger, months: list):
    months = set(months)
    likes = 0
    comments = 0
    counter = 0
    for post in posts:
        if post.date_str in months:
            likes += post.likes_count
            comments += post.comments_count
            counter += 1
    return util_methods.calculate_er(likes, comments, blogger, counter)


def coverage_method(posts: QuerySet[Post]):
    likes = 0
    comments = 0
    for post in posts[:12]:
        likes += post.likes_count
        comments += post.comments_count
    #     ((er12['likes'] + er12['comments']) // 12)
    result = util_methods.divide((likes + comments), 12)
    result = round_(result, 1)
    return result


def advertisement_price_method(posts: QuerySet[Post], blogger: Blogger):
    def cost_blogger():
        avg_likes, avg_comments = 0, 0
        size = len(posts)
        for post in posts:
            avg_comments += post.comments_count
            avg_likes += post.likes_count

        avg_comments = avg_comments / size
        avg_likes = avg_likes / size

        data = (avg_comments + avg_likes) / blogger.dt * 100

        if 1.5 <= data <= 3:
            return 5
        elif 3 < data <= 5:
            return 7
        elif 5 < data <= 8:
            return 10
        elif data > 8:
            return 15
        else:
            return 3.5

    tr = cost_blogger()
    dt = blogger.default_total / 1000

    result = tr * dt
    return round(result, 2)


def default_engagement_rate(posts: List[Post], blogger: Blogger):
    posts = posts[:12]
    likes_count = 0
    comments_count = 0
    counter = 0
    for post in posts:
        likes_count += post.likes_count
        comments_count += post.comments_count
        counter += 1

    return util_methods.calculate_er(likes_count, comments_count, blogger, counter)
