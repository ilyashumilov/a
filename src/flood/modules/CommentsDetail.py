import requests

from flood.modules.BaseFloodModel import BaseFloodModel
from main.models import Comment, Post
from parsing.AsyncParsingNew.utils import time_print


class CommentsDetail(BaseFloodModel):

    # blogger_login as post_id
    @classmethod
    async def from_file(cls, response: requests.Response, post_id: str):
        response.encoding = 'utf-8'
        comments_dct = {}
        counter = 0
        post = Post.objects.get(post_id=post_id)

        for line in response.iter_lines(chunk_size=10_000, decode_unicode=True):
            line: str

            try:
                commentator_id, commentator_login, comment_id, text = line.split(':', maxsplit=3)

                t = Comment(post_id=post.id, text=text, comment_id=comment_id,
                            commentator_social_id=commentator_id, commentator_login=commentator_login)
                comments_dct[comment_id] = t

                counter += 1

            except Exception as e:
                print(e)

            if counter % 10_000 == 0 and counter > 0:
                time_print(post_id, counter)
                await CommentsDetail.check_and_flood(comments_dct.copy())
                comments_dct.clear()
                time_print(post_id, counter, 'flooded')

        time_print(post_id, counter, 'flood final')
        await CommentsDetail.check_and_flood(comments_dct)

    @staticmethod
    async def check_and_flood(comments_dct: dict):
        comments_exist = Comment.objects.filter(comment_id__in=list(comments_dct.keys()))
        for comment in comments_exist:
            try:
                del comments_exist[comment.comment_id]
            except:
                pass
        time_print('comments count', len(comments_dct))
        Comment.objects.bulk_create(list(comments_dct.values()), batch_size=5_000, ignore_conflicts=True)
