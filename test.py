import asyncio

import aiohttp
import requests


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]



async def fonetika(tid: int):
    url = f'https://instaparser.ru/api.php?key=9vVV83uE6x7976K8&mode=finish&tid={tid}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(await resp.text())




async def main():
    url = "https://instaparser.ru/api.php?key=9vVV83uE6x7976K8&mode=status&status=1"
    json = requests.get(url).json()
    tasks = json['tasks']
    tids = []
    for i in tasks:
        tids.append(i['tid'])
    size=len(tids)
    for mini in chunks(tids, 100):
        await asyncio.gather(*[fonetika(t) for t in mini])


if __name__ == '__main__':
    # import uvloop




    # uvloop.install()
    # asyncio.run(main())
    loop=asyncio.get_event_loop()
    loop.run_until_complete(main())

