import string
import sys
import time
from decimal import Decimal

from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone

from api.extra import create_photo_link
from api.models import ProceedBlogger
from api.services import methods, process_service
from api.services import extra_service as es
from api.services.graph_service_v2 import Graph
from api.services.methods import timeit
from main.models import Post, Blogger
from main.services import capwords

SOCIALS = {'tiktok': 5, 'instagram': 3}


class StatisticMethods:

    def __init__(self, post_query, blogger, subscribers, blogger_simple):
        self.post_query: QuerySet[Post] = post_query
        self.blogger: Blogger = blogger
        self.simple_blogger: Blogger = blogger_simple
        self.proceed_subscribers = subscribers
        self.graph = Graph(self.simple_blogger, subscribers)
        self.avatar = methods.create_avatar_photo_link(blogger)

        self.functions = {
            'involvement_er': self.process_involvement_er_method,
            'posts_months': self.process_post_months_method,
            'comments_by_post': self.process_comments_by_post,
            'likes_by_post': self.process_likes_by_post,
            'best_time_to_publish': self.process_best_time_to_publish,
        }

    def another_socials(self):
        data = dict(self.simple_blogger.another_socials)
        another_socials = {}
        for social_name, login in data.items():
            try:
                blg = Blogger.objects.get(login=login, social_network_type_id=SOCIALS[social_name])
                t = another_socials[social_name] = {}
                t['login'] = capwords(blg.login)
                t['photo'] = create_photo_link(blg.avatar)
                t['name'] = capwords(str(blg.name))
                t['category'] = blg.category
                gender = None
                if blg.gender == 'f':
                    gender = 'female'
                elif blg.gender == 'm':
                    gender = 'male'
                t['gender'] = gender
                t['default_total'] = blg.default_total
                t['er'] = blg.er
            except:
                pass
        return another_socials

    def all_by_one_cycle(self):
        months = methods.get_last_months(6)
        involvement_er_dict = es.create_dct_for_graph()
        posts_months_dict = es.create_dct_for_graph()
        comments_by_post_dict = es.create_dct_for_graph()
        likes_by_post_dict = es.create_dct_for_graph()
        best_time_to_publish_dct = {}
        the_most_popular_posts = []

        blogger_data = {
            "blogger_id": self.blogger.id,
            'avatar': self.avatar,
            "posts_count": self.blogger.post_default_count,
            "likes_count": 0,
            "comments_count": 0,
            "subscribers_count": self.blogger.default_total,
            "following_count": self.blogger.following,
            'age': self.simple_blogger.age,
            'gender': None if self.blogger.gender is None else self.blogger.gender.name,
            'name': self.simple_blogger.name_capitalized,
            'status': None if self.blogger.status is None else self.blogger.status.name,
            'account_creation_date': es.date_to_front_date(self.blogger.account_creation_date),
            'parsing': {
                'status': self.simple_blogger.parsing_status,
                'refreshing': self.simple_blogger.parsing_measurement,
                'updated_at': es.date_to_front_datetime(timezone.now())
            },
            '__er': self.blogger.er,
            "another_socials": self.another_socials(),
            'updated_at': es.date_to_front_datetime(self.blogger.parsing_updated_at),
        }
        try:
            tags_in_posts = {}

            er12 = {}
            size = 0
            words = set()
            posts_query_list = list(self.post_query.order_by('-date'))

            for index, post in enumerate(posts_query_list):
                methods.involvement_er_method_new(post, involvement_er_dict, months)
                methods.posts_months_method(post, posts_months_dict)
                methods.comments_by_post_new(post, comments_by_post_dict, months)
                methods.likes_by_post_new(post, likes_by_post_dict, months)
                methods.best_time_to_publish(post, self.blogger, best_time_to_publish_dct)
                methods.blogger_data_method(post, blogger_data)
                methods.tags_in_posts_method(post, tags_in_posts)
                methods.text_filter(post.text, words)
                methods.top_3_advertising_posts(post, the_most_popular_posts)
                # last_advertiser = methods.last_advertisers_method(post, last_advertiser)

                methods.er12_method(post, er12, index)
                size = index
            size += 1
            er12__final = methods.calculate_er_new(er12['likes'], er12['comments'], self.blogger, 12)

            blogger_data['er12__global'] = er12__final
            # blogger_data['er'] = er12__final
            # blogger_data['__er'] = er12__final
            self.blogger.engagement_rate = Decimal(er12__final)
            self.blogger.save(update_fields=['engagement_rate'])

            the_most_popular_posts = sorted(the_most_popular_posts,
                                            key=lambda x: x['__sum_likes_comments'],
                                            reverse=True)

            comments_by_post_dict = self.process_comments_by_post(comments_by_post_dict, months)
            likes_by_post_dict = self.process_likes_by_post(likes_by_post_dict, months)
            involvement_er_dict = self.process_involvement_er_method(involvement_er_dict, months)
            # best_time_to_publish_dct = self.process_best_time_to_publish(best_time_to_publish_dct, blg_data=blogger_data)
            best_time_to_publish_dct = self.process_best_time_to_publish_new(best_time_to_publish_dct, blogger_data)

            avg_likes = likes_by_post_dict.get('avg_likes', 1)
            avg_comments = comments_by_post_dict.get('avg_comments', 1)

            coverage = ((er12['likes'] + er12['comments']) // 12)
            print('likes comments', er12['likes'], er12['comments'])
            tags_in_posts = sorted(tags_in_posts.items(), key=lambda x: x[1], reverse=True)

            if not settings.LOCAL_PC:
                brands_words = methods.create_brands_dict(words)
                brand_affinity = sorted(list(brands_words.values()), key=lambda x: x['name'])
            else:
                brand_affinity = {}
            graph_data = self.graph.all()
            try:
                emotions_graph, emoji, profanity_dct = methods.comment_graph(self.post_query)
            except Exception as e:
                emotions_graph = {}
                emoji = {}
                profanity_dct = {"use": 0, 'not_use': 0}

            involvement_er_dict['er'] = blogger_data['__er']
            try:
                result = {
                    **blogger_data,
                    **graph_data,
                    'involvement_er': involvement_er_dict,
                    'posts_months': posts_months_dict,
                    'comments_by_post': comments_by_post_dict,
                    'likes_by_post': likes_by_post_dict,
                    'best_time_to_publish': best_time_to_publish_dct,
                    'tags_in_posts': tags_in_posts,
                    'the_most_popular_posts': the_most_popular_posts,
                    'five_last_advertisers': self.process_last_advertiser(),
                    # 'five_last_advertisers': last_advertiser,
                    'brand_affinity': brand_affinity,
                    "er12": er12__final,
                    "test__er12": methods.calculate_er_new__test(er12['likes'], er12['comments'], self.blogger),
                    'avg_likes': avg_likes,
                    'avg_comments': avg_comments,
                    'relevant_bloggers': methods.relevant_bloggers(self.blogger),
                    'involvement': methods.calculate_er_new(avg_likes, avg_comments, self.blogger,
                                                            self.post_query.count()),
                    'coverage': coverage,
                    'advertisement_price': methods.calculate_price(self.blogger, avg_likes, avg_comments),
                    'audience_count': graph_data['audience_quality'].get('__quality_subscribers_count', avg_likes),

                    'words_in_bio': methods.words_in_bio_subscribers(self.proceed_subscribers),
                    'comments_emotions_graph': emotions_graph,
                    "comments_emojis": emoji,
                    'profanity': profanity_dct
                }
                methods.get_global_time()

                return result
            except Exception as e:
                print(e)
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
                return {**blogger_data}
        except Exception as e:
            print(e)
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            return {**blogger_data}

    def function_by_name(self, name, start=None, end=None):
        if name in self.functions:
            if start is not None:
                start = methods.text_to_date(start)
            if end is not None:
                end = methods.text_to_date(end)
            return self.functions[name](start=start, end=end)
        return {'message': 'not found'}

    def process_involvement_er_method(self, dct: dict, months):
        return process_service.process_involvement_er_method(self.post_query, self.blogger, dct, months)

    def process_post_months_method(self, dct: dict = None, start=None, end=None):
        return process_service.process_post_months_method(self.post_query, dct, start, end)

    def process_comments_by_post(self, dct: dict, months):
        return process_service.process_comments_by_post(self.post_query, dct, months)

    def process_likes_by_post(self, dct: dict, months):
        return process_service.process_likes_by_post(self.post_query, dct, months)

    def process_best_time_to_publish(self, dct: dict = None, start=None, end=None, blg_data: dict = None):
        return process_service.process_best_time_to_publish(self.post_query, self.blogger, dct, start, end, blg_data)

    def process_best_time_to_publish_new(self, dct: dict, blg_data: dict):
        return process_service.process_best_time_to_publish_new(dct, blg_data['posts_count'],
                                                                blg_data['likes_count'],
                                                                blg_data['comments_count'],
                                                                blg_data['er12__global']
                                                                )

    def process_top_3_advertising_posts(self, words_brands: dict):
        return process_service.process_top_3_advertising_posts(self.post_query, words_brands)

    # def process_last_advertiser(self, last_advertiser: list):
    #     return process_service.process_last_advertiser(self.blogger, last_advertiser)
    def process_last_advertiser(self):
        return process_service.process_last_advertiser_new(self.blogger, self.post_query.order_by('-date'))
