from typing import List

import requests

from api.services import methods
from flood.modules.BaseFloodModel import BaseFloodModel
from flood.modules.TaskCreator import TaskCreator
from flood.services.global_service import url_normalize
from flood.services.post_service import extract_all_posts
from main.models import Blogger, Post
from parsing.AsyncParsingNew.utils import time_print
from parsing.NovemberParsing.url_to_s3 import UrlToS3


class PostsDetail(BaseFloodModel):
    @classmethod
    async def from_file(cls, response: requests.Response, blogger_login: str):
        response.encoding = 'utf-8'
        if response.status_code == 404:
            return

        blogger = Blogger.objects.get(login=blogger_login, social_network_type_id=3)
        posts_dct = extract_all_posts(response.text)
        time_print(blogger_login, 'posts count', len(posts_dct))

        # deleted_query = (Q(blogger_id=blogger.id) & (~Q(post_id__in=list(posts_dct.keys()))))
        deleted_posts_dct = {}
        for post in Post.objects.filter(blogger=blogger):
            deleted_posts_dct[post.post_id] = post

        # Post.objects.bulk_update(deleted_posts, fields=['is_deleted'], batch_size=5_000)

        exists_posts = Post.objects.filter(post_id__in=list(posts_dct.keys()))
        time_print(blogger_login, 'exists count', len(exists_posts))
        photos = {}

        posts_to_create = []
        text_arr = []

        for post in exists_posts:
            from_dct = posts_dct[post.post_id]

            post.photos_url = f"{post.post_id}__{blogger.social_id}"
            photos[from_dct[2]] = url_normalize(post.photos_url)

            post.text = from_dct[3]
            post.likes_count = from_dct[4]
            post.comments_count = from_dct[5]
            post.views_count = from_dct[7]
            post.is_deleted = False

            text_arr.append(post)

            try:
                del posts_dct[post.post_id]
            except:
                pass
            try:
                del deleted_posts_dct[post.post_id]
            except:
                pass

        deleted_posts = Post.objects.filter(post_id__in=list(deleted_posts_dct.keys()))
        for del_post in deleted_posts:
            del_post.is_deleted = True
        time_print(blogger_login, 'deleted update', len(deleted_posts))
        Post.objects.bulk_update(deleted_posts, fields=['is_deleted'], batch_size=5_000)
        time_print(blogger_login, 'update count', len(exists_posts))

        Post.objects.bulk_update(exists_posts,
                                 fields=['photos_url', 'text', 'likes_count', 'comments_count', 'is_deleted',
                                         'views_count'],
                                 batch_size=5_000)
        for value in posts_dct.values():
            photo_url = f"{value[0]}__{blogger.social_id}"
            photos[value[2]] = url_normalize(photo_url)
            if value[6] is None:
                print('---------------==-=-=-')
                print(value)

            t = Post(blogger_id=blogger.id, post_id=value[0], post_login=value[1], photos_url=photo_url, text=value[3],
                     likes_count=value[4], comments_count=value[5], date=value[6], views_count=value[7])

            text_arr.append(t)

            posts_to_create.append(t)

        time_print(blogger_login, 'create count', len(posts_to_create))
        Post.objects.bulk_create(posts_to_create, batch_size=5_000)

        time_print(blogger_login, 'photos count', len(photos))



        print('UrlToS3.downloader_without_limit')

        await UrlToS3.downloader_without_limit(photos)

        try:
            task, cr = TaskCreator.create_parsing_task(None)
            logins__ = PostsDetail.process_advertisers(text_arr, blogger_login)
            TaskCreator.filtering_bloggers(task, logins__)

            print('advertisers set', len(logins__))
        except Exception as e:
            print(e, 'advertisers set')
        try:
            blogger.engagement_rate = blogger.create_er()
            blogger.save(update_fields=['engagement_rate'])
            print('done er12')
        except:
            pass

    @classmethod
    def process_advertisers(cls, posts: List, blogger_login):
        arr = set()
        for post in posts:
            t_dct = methods.last_advertisers_method_new(post)
            for n in t_dct.keys():
                if n == blogger_login:
                    continue
                arr.add(n)
        return list(arr)

    @classmethod
    def get_er_12(cls, posts: List[Post], blogger: Blogger):
        posts = sorted(posts, key=lambda x: x.date, reverse=True)[:12]
        likes = 0
        comments = 0
        for post in posts:
            likes += post.likes_count
            comments += post.comments_count
        engagement_rate = methods.calculate_er_new(likes, comments, blogger, 12)
        return engagement_rate
