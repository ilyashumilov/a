import asyncio
import platform
import time
from datetime import datetime
from typing import List

import asyncpg
import httpx
import typing

import requests

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]





def check_platform():
    if platform.system() == "Windows":
        return False
    else:
        return True


def create_loop():
    if check_platform():
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    return asyncio.get_event_loop()


def create_new_loop():
    return asyncio.new_event_loop()


def time_print(*args):
    print(*args, 'time:', datetime.now().strftime('%H:%M %d.%m'))


async def create_pool(db: dict) -> asyncpg.Pool:
    pool: asyncpg.Pool = await asyncpg.create_pool(user=db['USER'],
                                                   password=db['PASSWORD'],
                                                   database=db['NAME'],
                                                   host=db['HOST'],
                                                   min_size=1,
                                                   max_size=5
                                                   )
    return pool


async def select_data(pool: asyncpg.Pool, query, *args):
    async with pool.acquire() as connection:
        async with connection.transaction():
            connection: asyncpg.Connection
            result: List[asyncpg.Record] = await connection.fetch(query, *args)
            return result


async def select_one(pool: asyncpg.Pool, query, *args):
    async with pool.acquire() as connection:
        async with connection.transaction():
            connection: asyncpg.Connection
            result = await connection.fetchval(query, *args)
            return result


async def execute_many(pool: asyncpg.Pool, query, array: List[tuple]):
    async with pool.acquire() as connection:
        async with connection.transaction():
            connection: asyncpg.Connection
            await connection.executemany(query, array)


async def select_without_scan(pool: asyncpg.Pool, query, *args):
    async with pool.acquire() as connection:
        async with connection.transaction():
            connection: asyncpg.Connection
            await connection.execute('set enable_seqscan = FALSE;')
            result = await connection.fetchval(query, *args)
            await connection.execute('set enable_seqscan = TRUE;')
            return result


async def select_data_one_column_to_set(pool: asyncpg.Pool, query, *args):
    data = await select_data(pool, query, *args)
    return set(list(i[0] for i in data))


async def select_data_one_column_chunks(pool: asyncpg.Pool, query, limit, *args):
    data = await select_data(pool, query, *args)
    return chunks(list(i[0] for i in data), limit)


async def copy_to_db(pool: asyncpg.Pool, table: str, records: List[tuple], columns: list):
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.copy_records_to_table(table,
                                                   records=records,
                                                   columns=columns
                                                   )


async def save_tid(pool: asyncpg.Pool, query, tid: int):
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(query, tid)


async def execute_sql(pool: asyncpg.Pool, query):
    async with pool.acquire() as connection:
        async with connection.transaction():
            return await connection.execute(query)


async def fetch_iterator(url: str):
    return requests.get(url)


async def fetch_json(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()


async def get_done_tasks(parser: dict, task_prefix: str, task_name: str):
    url = f'{parser["base_url"]}api.php?key={parser["api_key"]}&mode=status&status=3'
    # if parser_type == 2:
    #     response = await fetch_json(url)
    # else:
    response = requests.get(url).json()
    if 'tasks' not in response:
        print('error in resp')
        time.sleep(10)
        return [], []
    tasks = []
    tids = []
    for task in response['tasks']:
        tid: int = task['tid']
        name: str = task['name']
        if not name.startswith(task_prefix):
            continue

        name = name.replace(task_name, '', 1).strip()
        tasks.append((tid, name))
        tids.append(tid)
    return tasks, tids


def get_done_tasks_sync(parser: dict, task_prefix: str, task_name: str):
    url = f'{parser["base_url"]}api.php?key={parser["api_key"]}&mode=status&status=3'
    print(parser['id'], url)
    # if parser_type == 2:
    #     response = await fetch_json(url)
    # else:
    response = requests.get(url, timeout=60).json()
    if 'tasks' not in response:
        print('error in resp')
        time.sleep(10)
        return [], []
    tasks = []
    tids = []
    for task in response['tasks']:
        tid: int = task['tid']
        name: str = task['name']
        if not name.startswith(task_prefix):
            continue

        name = name.replace(task_name, '', 1).strip()
        tasks.append((tid, name))
        tids.append(tid)
    return tasks, tids


async def download(tid, parser: dict) -> httpx.Response:
    while True:
        try:
            url = f'{parser["base_url"]}api.php?key={parser["api_key"]}&mode=result&tid={tid}'
            response = await fetch_iterator(url)
            return response
        except Exception as e:
            print(e)
            await asyncio.sleep(60)
            continue
