import requests

from intercalation.base_modules.BaseFloodModel import BaseFloodModel
from main.models import Post, Like
from parsing.ParsingModules.ParsingModule import time_print


class LikesFlood(BaseFloodModel):
    @classmethod
    async def from_file(cls, response: requests.Response, post_id: str):
        response.encoding = 'utf-8'
        likes_dct = {}
        counter = 0
        post_id = Post.objects.get(post_id=post_id).id

        for line in response.iter_lines(chunk_size=10_000, decode_unicode=True):
            line: str
            social_id, login = line.split(':')

            likes_dct[social_id] = login

            if counter % 10_000 == 0 and counter > 0:
                time_print(post_id, counter)
                cls.check_and_flood(likes_dct.copy(), post_id)
                likes_dct.clear()
                time_print(post_id, counter, 'flooded')

        time_print(post_id, counter, 'flood final')
        cls.check_and_flood(likes_dct.copy(), post_id)

    @classmethod
    def check_and_flood(cls, dct: dict, post_id):
        likes_exists = Like.objects.filter(post_id=post_id, social_id__in=list(dct.keys()))
        for i in likes_exists:
            del dct[i.social_id]

        arr = []
        for social_id, login in dct.items():
            arr.append(
                Like(social_id=social_id, login=login, post_id=post_id)
            )
        Like.objects.bulk_create(arr, ignore_conflicts=True)
