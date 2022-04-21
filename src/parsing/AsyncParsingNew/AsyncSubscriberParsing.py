import typing

import httpx
import requests

from parsing.AsyncParsingNew import utils, queries
from parsing.AsyncParsingNew.AsyncParsingModule import AsyncParsingModule


class AsyncSubscriberParsing(AsyncParsingModule):
    def __init__(self):
        super().__init__()
        self.parsing_method = 2
        self.task_prefix = 'subs-prod'
        self.task_name = f'{self.task_prefix}: '
        self.LIMIT = 10_000
        self.columns = ['social_id', 'login', 'blogger_id']
        self.table = 'subscriber'

    async def check_and_push(self, dct: dict, blogger_id: int, chunk_index):
        exists_ids = await utils.select_data_one_column_to_set(self.pool,
                                                               queries.SUBSCRIBERS_EXISTS,
                                                               blogger_id, list(dct.keys()))
        to_push = []
        for _id, _login in dct.items():
            if _id not in exists_ids:
                to_push.append((_id, _login, blogger_id))
        await utils.copy_to_db(self.pool, self.table, to_push, self.columns)
        utils.time_print('pushed', len(to_push), 'before clean', len(dct), 'blogger_id:', blogger_id,
                         'chunk', chunk_index)

    async def push_to_db(self, response: requests.Response, blogger_id: int):
        try:
            counter = 0
            chunk_index = 0
            dct = {}
            flag = False
            for chunk in response.iter_lines(chunk_size=10_000, decode_unicode=True):

                line = chunk.replace('\n', '').replace('\x00', '')
                if not flag and len(line.split(':')) < 2:
                    print('FLAG::',line)
                    return 'flag'
                elif not flag:
                    flag = True

                _id, _login = line.split(':')
                _id = int(_id)
                dct[_id] = _login
                counter += 1
                if counter > 0 and counter % self.LIMIT == 0:
                    chunk_index += 1
                    await self.check_and_push(dct, blogger_id, chunk_index)
                    dct.clear()
            if len(dct) > 0:
                chunk_index += 1
                await self.check_and_push(dct, blogger_id, chunk_index * self.LIMIT + len(dct))
                dct.clear()
            utils.time_print('done', 'blogger_id:', blogger_id, 'size', counter)
        except Exception as e:
            print(e)
            return 'error'
