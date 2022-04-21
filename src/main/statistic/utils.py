
import requests
from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractWeekDay
from django.utils import timezone

from main.enum import WeekDayEnum
from main.models import Post
from main.statistic.extra import plus_to_date_by_months, texts_to_words
from main.utils import posts_to_dict_in_array, post_to_dict
from django.conf import settings


class StatisticMethods:
    def __init__(self, blogger_login: str):
        self.login = blogger_login
        self.post_query = Post.objects.filter(blogger__login=self.login)

    
    def likes_count(self, _slice=None):
        if _slice is None:
            return sum(list(self.post_query.values_list('likes_count', flat=True)))
        return sum(list(self.post_query[:_slice].values_list('likes_count', flat=True)))

    
    def comments_count(self, _slice=None):
        if _slice is None:
            return sum(list(self.post_query.values_list('likes_count', flat=True)))
        return sum(list(self.post_query[:_slice].values_list('likes_count', flat=True)))

    
    def subscribers_count(self):
        return self.subscriber_query.count()

    
    def posts_count(self):
        return self.post_query.count()

    
    def avg_comments(self, _slice=None):
        if _slice is None:
            return self.post_query.aggregate(Avg('comments_count'))['comments_count__avg']
        return self.post_query[:_slice].aggregate(Avg('comments_count'))['comments_count__avg']

    
    def avg_likes(self, _slice=None):
        if _slice is None:
            return self.post_query.aggregate(Avg('likes_count'))['likes_count__avg']
        return self.post_query[:_slice].aggregate(Avg('likes_count'))['likes_count__avg']

    
    def avg_count_of_posts_by_months(self, _slice=None):
        months = self.post_query.annotate(month=TruncMonth('date')).values('month')
        if _slice is None:
            posts = months.annotate(total=Count('id'))
        else:
            posts = months[:_slice].annotate(total=Count('id'))

        count_of_months = len(posts)
        sum_count_posts = 0
        for post in posts:
            sum_count_posts += post['total']
        return sum_count_posts / count_of_months

    def hashtags_from_posts(self):
        text_array = self.post_query.values_list('text', flat=True)
        hashtags = {}

        for text in text_array:
            for word in text.split():
                if word[0] == '#':
                    hashtag = word[1:]
                    if hashtag not in hashtags:
                        hashtags[hashtag] = 1
                    hashtags[hashtag] += 1

        return sorted(hashtags.items(), key=lambda x: x[1], reverse=True)[:5]

    def popular_day_and_hour(self):
        posts = self.post_query.annotate(weekday=ExtractWeekDay("date"))
        days = {}
        for day in WeekDayEnum:
            days[day.value] = {"posts": [], 'avg_likes': 0, 'avg_comments': 0}
        for post in posts:
            days[post.weekday]['posts'].append(post)
        for day in WeekDayEnum:
            avg_likes = 0
            avg_comments = 0
            current_day = days[day.value]
            for post in current_day['posts']:
                post: Post
                avg_likes += post.likes_count
                avg_comments += post.comments_count
            avg_likes = avg_likes / len(current_day['posts'])
            avg_comments = avg_comments / len(current_day['posts'])
            current_day['avg_likes'] = avg_likes
            current_day['avg_comments'] = avg_comments
        a = {k: v for k, v in
             sorted(days.items(), key=lambda item: (item[1]['avg_likes'], item[1]['avg_comments']), reverse=True)}
        key = list(a.keys())[0]

        print(a.keys())
        for i in list(a.items()):
            print(i[0], i[1]['avg_comments'], i[1]['avg_likes'], len(i[1]['posts']))

        popular_day = WeekDayEnum(key).name
        posts = [post for post in
                 sorted(days[key]['posts'], key=lambda x: (x.likes_count, x.comments_count), reverse=True)]
        popular_hour = posts[0].date.hour
        return popular_day, popular_hour

    def brand_affinity(self):
        posts = list(self.post_query.values_list('id', 'text'))
        posts_dict = []
        for post in posts:
            posts_dict.append(
                {'id': post[0], 'text': post[1]}
            )

        data = requests.post(f'http://{settings.ELASTIC}/search-brands-posts/', json=posts_dict)
        data = data.json()['data']
        posts = self.post_query.filter(id__in=data)

        return posts_to_dict_in_array(list(posts))

    def count_advertising_posts(self):
        posts = self.post_query.filter(text__contains='@').order_by('-date')
        first_post_date = posts[0].date

        months = [plus_to_date_by_months(first_post_date, 1),
                  plus_to_date_by_months(first_post_date, 3),
                  plus_to_date_by_months(first_post_date, 6),
                  plus_to_date_by_months(first_post_date, 12)
                  ]
        months_counters = [0, 0, 0, 0]

        for post in posts:
            post: Post
            for i in range(len(months)):
                if post.date >= months[i]:
                    months_counters[i] += 1
        size = len(posts)
        for i in range(len(months_counters)):
            months_counters[i] = months_counters[i] / size
        return months_counters

    def five_last_advertisers(self):
        advertisers = set()
        q = Q(text__contains='@')
        __iterator = self.post_query.filter(q).values_list('text', flat=True).order_by('-date')
        for post_text in __iterator:
            for word in post_text.split():
                if word[0] == '@':
                    advertisers.add(word[1:])
                if len(advertisers) >= 5:
                    return list(advertisers)

        return list(advertisers)

    def the_most_popular_post(self):
        post = self.post_query.order_by('-likes_count', '-comments_count').first()
        return post_to_dict(post)

    def relevant_bloggers(self):
        return

    def audience_quality(self):
        posts = list(self.post_query.order_by('-date')[:10].values_list('likes_count', flat=True))
        avg_likes = sum(posts) / len(posts)
        return round((avg_likes / self.subscribers_count()), 2)

    def audience_count(self):
        posts = list(self.post_query.order_by('-date')[:10].values_list('likes_count', flat=True))
        avg_likes = sum(posts) // len(posts)
        return avg_likes

    def advertisement_price(self):
        return self.subscribers_count() / 10000 * 10 * 70
