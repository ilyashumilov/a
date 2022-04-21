import time

import requests

from main.utils import from_line_to_data
from parsing.AsyncParsingMulti.AsyncParsingModule import AsyncParsingModule
from parsing.AsyncParsingNew import utils, queries


class AsyncPostParsing(AsyncParsingModule):
    def __init__(self, parser):
        super().__init__(parser)
        self.parsing_method = 1
        self.task_prefix = 'post-prod'
        self.task_name = f'{self.task_prefix}: '
        self.columns = ['post_id', 'post_login', 'photos_url', 'text',
                        'likes_count', 'comments_count', 'date', 'blogger_id']
        self.table = 'post'

    async def push_to_db(self, response: requests.Response, blogger_id: int):
        response.encoding = 'utf-8'
        lines = response.text.replace('\x00', '').strip().split('\n')
        if len(lines) < 1:
            return
        s = []
        post_dublicates = set()
        dct = {}
        st = time.monotonic()
        for line in lines:
            ln = line.strip().replace('\n', '')
            try:
                if ln.find(':https://instagram') > 0:
                    s.clear()
                s.append(ln)

                final_line = ''.join(s)
                try:
                    login_post, id_post, date, comments_count, \
                    likes_count, text, photos_url = from_line_to_data(final_line)
                    s.clear()


                except:
                    continue
                    pass
                if id_post in post_dublicates:
                    continue
                else:
                    post_dublicates.add(id_post)

                dct[id_post] = (id_post, login_post, photos_url, text,
                                likes_count, comments_count, date, blogger_id)


            except Exception as e:
                print(e)

        exists = await utils.select_data_one_column_to_set(self.pool, queries.POSTS_EXISTS,
                                                           blogger_id,
                                                           list(dct.keys()))
        to_push = []
        for i, v in dct.items():
            if i not in exists:
                to_push.append(v)
        try:
            await utils.copy_to_db(self.pool, self.table, to_push, self.columns)
        except Exception as e:
            print(e)
        utils.time_print('pushed', len(to_push), 'before', len(dct),
                         'blogger:', blogger_id, 'time', time.monotonic() - st)
