import typing
from decimal import Decimal

import requests

from intercalation.base_modules.BaseFloodModel import BaseFloodModel
from intercalation.services.posts_service import extract_all_posts, url_normalize
from intercalation.work_modules.TaskCreator import TaskCreator
from main.models import Blogger, Post
from parsing.NovemberParsing.url_to_s3 import UrlToS3
from parsing.ParsingModules.ParsingModule import time_print
from rest.api.social.methods import posts_methods

FILE_FROM = 'posts_lk_potok'


class PostsFlood(BaseFloodModel):
    @classmethod
    async def from_file(cls, response: requests.Response, blogger_login: typing.Optional[str]):
        response.encoding = 'utf-8'
        if response.status_code == 404:
            return
        posts_dct, login_post = extract_all_posts(response.text)
        posts_count = len(posts_dct)

        if not posts_count:
            return

        if blogger_login is None:
            social_id = login_post.split('_')[1]
            blogger, _ = Blogger.objects.get_or_create(social_id=social_id, social_network_type_id=3,
                                                       defaults={'file_from_info': FILE_FROM})
        else:
            blogger = Blogger.objects.get_default(login=blogger_login)

        blogger_login = blogger.login
        time_print(blogger_login, 'posts count', posts_count)

        deleted_posts_dct = {}
        for post in Post.objects.filter(blogger=blogger):
            deleted_posts_dct[post.post_id] = post

        # time_print(blogger_login, 'deleted posts count', len(deleted_posts_dct))

        photos = {}

        text_arr = []

        cls.process_exists_posts(posts_dct, deleted_posts_dct, blogger, photos, text_arr)
        cls.update_delete_posts(deleted_posts_dct, blogger)
        cls.process_create_posts(posts_dct, blogger, photos, text_arr)
        cls.process_after_flood(text_arr, blogger)

    @classmethod
    def process_exists_posts(cls, posts_dct: dict, deleted_posts_dct: dict, blogger: Blogger, photos: dict, text_arr):
        exists_posts = Post.objects.filter(post_id__in=list(posts_dct.keys()))
        time_print(blogger.login, 'exists count', len(exists_posts))

        for post in exists_posts:
            from_dct = posts_dct[post.post_id]

            post.photos_url = f"{post.post_id}__{blogger.social_id}"
            photos[from_dct[2]] = url_normalize(post.photos_url)

            post.text = from_dct[3]
            post.likes_count = from_dct[4]
            post.comments_count = from_dct[5]
            post.views_count = from_dct[7]
            post.is_deleted = False

            if post.blogger is None:
                post.blogger_id = blogger.id

            text_arr.append(post)

            try:
                del posts_dct[post.post_id]
            except:
                pass
            try:
                del deleted_posts_dct[post.post_id]
            except:
                pass
        Post.objects.bulk_update(exists_posts,
                                 fields=['text', 'likes_count', 'comments_count', 'views_count', 'is_deleted',
                                         'blogger_id'])
        time_print(blogger.login, 'update count', len(exists_posts))

    @classmethod
    def update_delete_posts(cls, deleted_posts_dct: dict, blogger: Blogger):
        deleted_posts = Post.objects.filter(post_id__in=list(deleted_posts_dct.keys()))
        for del_post in deleted_posts:
            del_post.is_deleted = True
        time_print(blogger.login, 'deleted posts', len(deleted_posts))
        Post.objects.bulk_update(deleted_posts, fields=['is_deleted'], batch_size=5_000)

    @classmethod
    def process_create_posts(cls, posts_dct: dict, blogger: Blogger, photos: dict, text_arr):
        posts_to_create = []
        for value in posts_dct.values():
            photo_url = f"{value[0]}__{blogger.social_id}"
            photos[value[2]] = url_normalize(photo_url)

            t = Post(blogger_id=blogger.id, post_id=value[0], post_login=value[1], photos_url=photo_url, text=value[3],
                     likes_count=value[4], comments_count=value[5], date=value[6], views_count=value[7])

            text_arr.append(t)

            posts_to_create.append(t)

        time_print(blogger.login, 'create count', len(posts_to_create))
        Post.objects.bulk_create(posts_to_create, batch_size=5_000)

        time_print(blogger.login, 'photos count', len(photos))

        time_print('time_print(UrlToS3.push_to_kafka(photos))')
        UrlToS3.push_to_kafka(photos)

    @classmethod
    def process_after_flood(cls, text_arr: list, blogger: Blogger):
        rejects = ('Инстаграм боты', 'lk_potok')
        for reject in rejects:
            if reject in blogger.file_from_info:
                return

        posts = sorted(text_arr, key=lambda x: x.date, reverse=True)
        try:
            task, cr = TaskCreator.create_parsing_task(None)
            logins = PostsFlood.process_advertisers(posts, blogger.login)
            TaskCreator.filtering_bloggers(task, logins, chunks_support=True,
                                           **dict(extra_info=dict(is_advertiser=True)))

            print('advertisers set', len(logins))
        except Exception as e:
            print(e, 'advertisers set')
        try:
            blogger.engagement_rate = Decimal(str(posts_methods.default_engagement_rate(posts, blogger)))
            blogger.save(update_fields=['engagement_rate'])
            print('done er12')
        except:
            pass

    @classmethod
    def process_advertisers(cls, posts: typing.List[Post], blogger_login):
        arr = set()
        for post in posts:
            t_dct = posts_methods.last_advertiser_method_v2(post.text)
            for n in t_dct.keys():
                if n == blogger_login:
                    continue
                arr.add(n)
        return list(arr)
