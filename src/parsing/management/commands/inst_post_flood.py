import asyncio

import requests
from django.conf import settings
from django.core.management import BaseCommand

# inst_post_flood
from main.models import AccountParser, Blogger
from parsing.NovemberParsing.flood_post_module import FloodPostModule

from parsing.NovemberParsing.flood_subscribers_module import FloodSubscriberModule
from parsing.NovemberParsing.service import from_line_to_data
from tortoise_base import SubscriberAsync, db_init, PostAsync


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        loop = asyncio.get_event_loop()
        loop.create_task(worker())
        loop.run_forever()


def download(tid: int, parser: AccountParser):
    while True:
        try:
            url = f'{parser.base_url}api.php?key={parser.api_key}&mode=result&tid={tid}'
            response = requests.get(url.format(tid))
            response.encoding = 'utf-8'
            return response
        except Exception as e:
            print(e, 'sleep')


async def worker():
    db = settings.DATABASES['default']
    await db_init(db)

    text = """justking31""".strip().split('\n')
    text = list(map(lambda x: x.strip(), text))

    text = set(text)
    fsm = FloodPostModule()
    parser = AccountParser.objects.get(login='hypepotok3')
    url = f'{parser.base_url}api.php?key={parser.api_key}&mode=status&status=3'
    data = requests.get(url).json()
    dct = {}
    for i in data['tasks']:
        if str(i['name']).endswith('_posts') and str(i['name']).replace('_posts', '') in text:
            name = i['name'].replace('_posts','')

            dct[name] = {
                'blogger_id': Blogger.objects.get(login=name).id,
                'social_id': Blogger.objects.get(login=name).social_id,
                'tid': i['tid']
            }
            text.remove(name)
    # print(len(dct), dct)
    for i, v in dct.items():
        try:
            response = download(v['tid'], parser)

            lines = response.text.replace('\x00', '').strip().split('\n')
            print(i, v, 'lines', len(lines))

            s = []
            posts_async = []
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
                        except Exception as e:
                            print(e)
                            continue
                            pass
                        photo = ''
                        for kk in photos_url.split(','):
                            if '.mp4' not in kk:
                                photo = kk
                                break
                        if photo == "" and len(photos_url.split(',')) > 0:
                            photo = photos_url.split(',')[0]
                        try:
                            post = PostAsync(blogger_id=v['blogger_id'], post_id=id_post, post_login=login_post,
                                             photos_url=photo,
                                             text=text, likes_count=likes_count, comments_count=comments_count,
                                             date=date
                                             )
                            posts_async.append(post)
                        except:
                            print('err')
                    except Exception as e:
                        print(e)

            await fsm.prepare_flood(posts_async, v['blogger_id'], v['social_id'])

        except Exception as e:
            print(e, i, v)
