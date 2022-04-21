from collections import ChainMap

from django.db.models import QuerySet

from main.models import Blogger, Post
from rest.api.social.methods import util_methods, posts_methods
from rest.api.social.methods.comments_methods import comments_method
from rest.decorators import local_pc_check, cacheable_db_data, timeit


class PostsService:
    def __init__(self, blogger: Blogger, language='ru'):

        self.blogger = blogger
        self.posts = Post.objects.filter_default(blogger)
        self.months = util_methods.get_with_last_non_zero_months_by_sorted_posts(self.posts, 6)
        self.language = language

    @timeit
    def posts_service(self):
        blogger = self.blogger
        posts = self.posts

        if len(posts) == 0:
            return {}

        result = ChainMap(
            self.involvement_engagement_rate_service(blogger, posts),
            self.posts_months_service(blogger, posts),
            self.comments_by_post_service(blogger, posts),
            self.likes_by_post_service(blogger, posts),
            self.best_time_to_publish_service(blogger, posts),
            self.tags_in_posts_service(blogger, posts),
            self.the_most_popular_posts_service(blogger, posts),
            self.last_advertisers_service(blogger, posts),
            self.brands_finder_service(blogger, posts),
            self.metrics_service(blogger, posts),
            self.involvement_service(blogger, posts),
            self.coverage_service(blogger, posts),
            self.advertisement_price_service(blogger, posts),
            self.comments_emoji_emotions_service(blogger, posts)
        )

        return dict(result)

    @timeit
    def involvement_engagement_rate_service(self, blogger: Blogger, posts: QuerySet[Post]):
        involvement_er_dict = {}
        try:
            result = posts_methods.involvement_engagement_rate_method(posts, blogger, involvement_er_dict, self.months)
        except Exception as e:
            print(e)
            result = {}
        return dict(involvement_er=result)

    @timeit
    def posts_months_service(self, blogger: Blogger, posts: QuerySet[Post]):
        posts_months_dict = {"__likes": 0, "__comments": 0}
        posts_methods.posts_months_method(posts, posts_months_dict)
        return dict(posts_months=posts_months_dict)

    @timeit
    def comments_by_post_service(self, blogger: Blogger, posts: QuerySet[Post]):
        comments_by_post_dict = {}
        posts_methods.comments_by_post_method(posts, comments_by_post_dict, self.months)
        return dict(comments_by_post=comments_by_post_dict)

    @timeit
    def likes_by_post_service(self, blogger: Blogger, posts: QuerySet[Post]):
        likes_by_post_dict = {}
        posts_methods.likes_by_post_method(posts, likes_by_post_dict, self.months)
        return dict(likes_by_post=likes_by_post_dict)

    @timeit
    def best_time_to_publish_service(self, blogger: Blogger, posts: QuerySet[Post]):
        best_time_to_publish_dict = {}
        posts_methods.best_time_to_publish_method(posts, best_time_to_publish_dict, blogger)
        return dict(best_time_to_publish=best_time_to_publish_dict)

    @timeit
    def tags_in_posts_service(self, blogger: Blogger, posts: QuerySet[Post]):
        tags_in_posts_dict = {}
        posts_methods.tags_in_posts_method(posts, tags_in_posts_dict)
        # tags_in_posts = list(tags_in_posts_dict.items())
        tags_in_posts = sorted(tags_in_posts_dict.items(), key=lambda x: x[1], reverse=True)
        return dict(tags_in_posts=tags_in_posts)

    @timeit
    def the_most_popular_posts_service(self, blogger: Blogger, posts: QuerySet[Post]):
        the_most_popular_posts_array = []
        posts_methods.the_most_popular_posts(posts, the_most_popular_posts_array)

        the_most_popular_posts_array = sorted(the_most_popular_posts_array,
                                              key=lambda x: x['__sum_likes_comments'],
                                              reverse=True)
        return dict(the_most_popular_posts=the_most_popular_posts_array)

    @timeit
    def last_advertisers_service(self, blogger: Blogger, posts: QuerySet[Post]):
        five_last_advertisers_dict = posts_methods.last_advertisers(posts, blogger, self.language)

        return dict(five_last_advertisers=five_last_advertisers_dict)

    @timeit
    @local_pc_check
    def brands_finder_service(self, blogger: Blogger, posts: QuerySet[Post]):
        try:
            brands_words = posts_methods.brand_affinity(posts, self.language)
            brand_affinity = sorted(list(brands_words.values()), key=lambda x: x['name'])
            return dict(brand_affinity=brand_affinity)
        except Exception as e:
            print(e)
            return {'brand_affinity': {}}

    @timeit
    def metrics_service(self, blogger: Blogger, posts: QuerySet[Post]):
        return posts_methods.metrics_method(posts, blogger)

    @timeit
    def involvement_service(self, blogger: Blogger, posts: QuerySet[Post]):
        return dict(involvement=posts_methods.involvement_method(posts, blogger, self.months))

    @timeit
    def coverage_service(self, blogger: Blogger, posts: QuerySet[Post]):
        return dict(coverage=posts_methods.coverage_method(posts))

    @timeit
    def advertisement_price_service(self, blogger: Blogger, posts: QuerySet[Post]):
        return dict(advertisement_price=posts_methods.advertisement_price_method(posts, blogger))

    @timeit
    @local_pc_check
    @cacheable_db_data
    def comments_emoji_emotions_service(self, blogger: Blogger, posts: QuerySet[Post]):
        emotions_graph, emoji, profanity_dct = comments_method(posts, util_methods.get_last_month_post(posts, 6),
                                                               self.language)
        return dict(comments_emotions_graph=emotions_graph, comments_emojis=emoji, profanity=profanity_dct)
