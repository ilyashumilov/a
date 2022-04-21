import time

import requests
from django import db
from django.db.models import Q

from main.enum import MethodEnum
from main.models import AccountParser, Blogger, Post
from main.utils import from_line_to_data
from .ParsingModule import ParsingModule


class PostModule(ParsingModule):
    parsing_method: 1
    task_prefix: str = 'post-prod'

    def __init__(self):
        self.parsing_method = 1
        self.task_prefix = 'post-prod'

    def get_task_prefix(self):
        return f"{self.task_prefix}: "

    # override

    def create_dict(self, blogger_login, parser: AccountParser) -> list:
        dct = [('mode', 'p1'), ('name', f'{self.task_prefix}: {blogger_login}'), ('links', f"{blogger_login}"),
               ('act', '6'),
               ('limit', str(parser.limit)), ('limit2', '0'), ('privat', '0'), ('avatar', '0'), ('bus', '0'),
               ('verif', '0'), ('story', '0'), ('hstory', '0'), ('fol1', ''), ('fol2', ''), ('fols1', ''),
               ('fols2', ''), ('posts1', ''), ('posts2', ''), ('kfl1', '0.00'), ('kfl2', '0.00'), ('kfc1', '0.00'),
               ('kfc2', '0.00'), ('pratio1', '0.00'), ('pratio2', '0.00'), ('lastpost', '0'), ('white', ''),
               ('whitel', ''), ('stop', ''), ('stopl', ''), ('white2', ''), ('stop2', ''), ('catwhite', ''),
               ('whitecapwords', ''), ('postlk1', ''), ('postlk2', ''), ('postcm1', ''), ('postcm2', ''),
               ('web', '1'),
               ('white1t', '0'), ('stop1t', '0'), ('catwhitet', '0'), ('whitecapt', '0'), ('white2t', '0'),
               ('stope2t', '0'), ('spec[]', 3), ('spec[]', 4), ('spec[]', 5), ('spec[]', 8), ('spec[]', 9)]
        return dct

    def change_blogger_state(self, blogger: Blogger):
        blogger.in_process = True
        blogger.save()

    def check_parsed(self, blogger: Blogger):
        return Post.objects.filter(blogger=blogger)[:1].count() > 0

    def push_to_db(self, response: requests.Response, blogger: Blogger):
        to_create = []
        post_ids = set()

        lines = response.text.replace('\x00', '').strip().split('\n')
        print(blogger.login, 'lines', len(lines))

        s = []
        if len(lines) > 1:
            for line in lines:
                ln = line.strip().replace('\n', '')
                try:
                    if ln.find(':https://instagram') > 0:
                        s.clear()
                        s.append(ln)
                    else:
                        s.append(ln)

                    final_line = ''.join(s)
                    try:
                        login_post, id_post, date, comments_count, \
                        likes_count, text, photos_url = from_line_to_data(final_line)
                        s.clear()
                    except:
                        continue
                        pass

                    if id_post in post_ids:
                        # print('dublicate', id_post)
                        continue
                    else:
                        post_ids.add(id_post)
                    post = Post(blogger=blogger, post_id=id_post, post_login=login_post,
                                photos_url=photos_url, text=text, likes_count=likes_count,
                                comments_count=comments_count, date=date)
                    to_create.append(post)
                except Exception as e:
                    print(e)

        if len(lines) > 1:
            ids = [i.post_id for i in to_create]
            print('pre push')
            exist = set(
                list(Post.objects.filter(blogger_id=blogger.id, post_id__in=ids).values_list("post_id", flat=True)))
            to_create_new = []
            for i in to_create:
                if i.post_id in exist:
                    continue
                else:
                    to_create_new.append(i)

            print(len(to_create), len(to_create_new), 'from old to new')
            Post.objects.bulk_create(to_create_new, batch_size=10_000)
            to_create = []
            print('pushed')
            db.reset_queries()
        blogger.parsed = True
        blogger.save()

    def get_new_blogger(self):
        return Blogger.objects.filter(in_process=False).order_by('post_default_count', '-priority').first()
