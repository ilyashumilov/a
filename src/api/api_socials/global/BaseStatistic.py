from django.db.models import QuerySet

from main.models import Blogger, Post, Subscriber

from .methods import bloggers_methods as blg_methods
from .methods import subscribers_methods as subs_methods
from .methods import posts_methods as posts_methods


class BaseStatistic:
    def __init__(self, posts: QuerySet[Post], blogger: Blogger, subscribers: QuerySet[Subscriber]):
        self.posts = posts
        self.blogger = blogger
        self.subscribers = subscribers

    def blogger_block(self):
        blogger_data = blg_methods.blogger_info_method(self.blogger)
        return blogger_data

    def posts_block(self):
        index = 0

        blogger_data = self.blogger_block()

        months, involvement_er_dict, posts_months_dict, comments_by_post_dict, \
        likes_by_post_dict, best_time_to_publish_dct, the_most_popular_posts, \
        tags_in_posts, er12, words = posts_methods.pre_dicts_create_method()

        for post in self.posts:
            posts_methods.involvement_er_method(post, involvement_er_dict, months)
            posts_methods.posts_months_method(post, posts_months_dict)
            posts_methods.comments_by_post_method(post, comments_by_post_dict, months)
            posts_methods.likes_by_post_method(post, likes_by_post_dict, months)
            posts_methods.best_time_to_publish_method(post, self.blogger, best_time_to_publish_dct)
            posts_methods.likes_comments_method(post, blogger_data)
            posts_methods.tags_in_posts_method(post, tags_in_posts)
            posts_methods.text_filter_method(post, words)
            posts_methods.top_3_advertising_posts_method(post, the_most_popular_posts)
            posts_methods.er12_method(post, er12, index)
            index += 1
        size = index + 1

        pass

    def subscribers_block(self):
        subscribers_data = subs_methods.subscribers_all(self.blogger)
        return subscribers_data

    def comments_block(self):
        pass

    def result_block(self):
        pass
