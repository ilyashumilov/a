import asyncio
import time
import os
import aiohttp
import typing
import enlighten
import httpx

from parsing.AsyncParsingNew import queries, utils

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

db = {
    "USER": os.environ.get("DB_USER"),
    "PASSWORD": os.environ.get('DB_PASSWORD'),
    "HOST": os.environ.get('DB_HOST'),
    "NAME": os.environ.get('DB_NAME')
}


def create_pbar(manager, total, index):
    return manager.counter(total=total, desc=f'#{index}', unit='ticks')


class AsyncParsingModule(object):
    def __init__(self, parser):
        self.parsing_method: int = 1  # 1 - post , 2 - subscriber
        self.task_prefix: str = 'post-prod'  # post-prod , subs-prod
        self.task_name = f"{self.task_prefix}: "
        self.loop = utils.create_new_loop()

        self.wait_time = 10
        self.parser_id = parser

    async def parser_start(self):
        self.pool = await utils.create_pool(db)

        while True:
            manager = enlighten.get_manager()
            parser = (await utils.select_data(self.pool, queries.PARSER_BY_ID_QUERY, self.parser_id))[0]
            utils.time_print('started', 'with parser', parser)
            await self.coroutine(parser, manager)

            manager.stop()

    async def coroutine(self, parser: dict, manager):
        try:
            await self.__coroutine(parser, manager)
        except Exception as e:
            print(e, 'parser', parser['id'])

    async def __coroutine(self, parser: dict, manager):
        tasks, tids = utils.get_done_tasks_sync(parser, self.task_prefix, self.task_name)
        await asyncio.sleep(self.wait_time)
        tid_exists: set = await utils.select_data_one_column_to_set(self.pool, queries.TIDS_EXISTS, tids)
        if len(tid_exists) == len(tids):
            await asyncio.sleep(120)
            return
        print(len(tasks), parser['id'])


        print('tid exist', len(tid_exists), 'tid all', len(tids), 'parser', parser['id'])
        tasks_after_clean = []
        for task in tasks:
            if task[0] in tid_exists:
                continue
            tasks_after_clean.append(task)
        tasks_after_clean.sort(key=lambda x: x[0], reverse=True)
        pbar = create_pbar(manager, len(tasks_after_clean), parser['id'])
        for _task_ in tasks_after_clean:
            print(_task_, parser['api_key'])
            while True:
                st = time.monotonic()
                blogger_id = await utils.select_one(self.pool, queries.BLOGGER_ID_BY_LOGIN, _task_[1])

                response_iterator = await self.download(_task_[0], parser)
                try:
                    result = await self.push_to_db(response_iterator, blogger_id)
                except Exception as e:
                    print(e)
                    break
                if result == 'error':
                    await asyncio.sleep(60)
                    continue
                if result == 'flag':
                    break

                else:
                    # todo update blogger state
                    await utils.save_tid(self.pool, queries.TID_SAVE, _task_[0])
                    utils.time_print('monotonic', time.monotonic() - st, f'blogger: {blogger_id}')
                    pbar.update()
                    break

    async def download(self, tid, parser):
        return await utils.download(tid, parser)

    async def push_to_db(self, response, blogger_id: int):
        pass


if __name__ == '__main__':
    async def work(apm: AsyncParsingModule):
        await apm.get_parsers()


    apm = AsyncParsingModule()
    apm.loop.run_until_complete(work(apm))
