import time

import requests
from django import db

from main.models import AccountParser, Blogger, Subscriber
from main.utils import get_current_time
from .ParsingModule import ParsingModule


def check_and_push(to_create_ids, to_create):
    to_create_subs = []
    st = time.monotonic()
    ext = set(list(Subscriber.objects.filter(social_id__in=to_create_ids).values_list('social_id', flat=True)))
    print('got ext',time.monotonic()-st)
    for sub_key, value in to_create.items():
        if sub_key not in ext:
            to_create_subs.append(to_create[sub_key])

    Subscriber.objects.bulk_create(to_create_subs, ignore_conflicts=True)
    to_create_subs.clear()
    db.reset_queries()


class SubscriberModule(ParsingModule):
    parsing_method: 2
    task_prefix: str = 'subs-prod'

    def __init__(self):
        self.parsing_method = 2
        self.task_prefix = 'subs-prod'

    def get_task_prefix(self):
        return f"{self.task_prefix}: "

    # override

    def create_dict(self, blogger_login, parser: AccountParser) -> list:
        dct = [('mode', 'p1'), ('name', f'{self.task_prefix}: {blogger_login}'), ('links', str(blogger_login)),
               ('act', '1'), ('limit', str(parser.limit)),
               ('limit2', '0'), ('privat', '0'), ('avatar', '0'), ('bus', '0'), ('verif', '0'), ('story', '0'),
               ('hstory', '0'), ('fol1', ''), ('fol2', ''), ('fols1', ''), ('fols2', ''), ('posts1', ''),
               ('posts2', ''), ('kfl1', '0.00'), ('kfl2', '0.00'), ('kfc1', '0.00'), ('kfc2', '0.00'),
               ('pratio1', '0.00'), ('pratio2', '0.00'), ('lastpost', '0'), ('white', ''), ('whitel', ''),
               ('stop', ''), ('stopl', ''), ('white2', ''), ('stop2', ''), ('catwhite', ''), ('whitecapwords', ''),
               ('postlk1', ''), ('postlk2', ''), ('postcm1', ''), ('postcm2', ''), ('spec[]', '1'), ('spec[]', '2'),
               ('web', '1'), ('white1t', '0'), ('stop1t', '0'), ('catwhitet', '0'), ('whitecapt', '0'),
               ('white2t', '0'), ('stope2t', '0')]
        return dct

    def change_blogger_state(self, blogger: Blogger):
        blogger.subscribers_in_process = True
        blogger.save()

    def check_parsed(self, blogger: Blogger):
        return Subscriber.objects.filter(blogger=blogger)[:1].count() > 0

    def push_to_db(self, response: requests.Response, blogger: Blogger):
        LIMIT = 10_000
        st = time.monotonic()

        try:
            glb_counter = 0
            to_create = {}
            to_create_ids = []
            counter = 0
            for line in response.iter_lines(chunk_size=LIMIT, decode_unicode=True):
                line: str
                line = line.replace('\x00', '')
                _id, _login = line.split(':')
                to_create[_id] = Subscriber(social_id=_id, login=_login, blogger=blogger)
                to_create_ids.append(_id)

                counter += 1
                glb_counter += 1
                if counter >= LIMIT:
                    check_and_push(to_create_ids, to_create)
                    to_create_ids.clear()
                    to_create.clear()
                    counter = 0
                    print(glb_counter, 'chunk', blogger.login, 'time', time.monotonic() - st, 'now', get_current_time())
            check_and_push(to_create_ids, to_create)
            to_create_ids.clear()
            to_create.clear()
            print(glb_counter, 'all', blogger.login, 'time', time.monotonic() - st, 'now', get_current_time())


        except Exception as e:
            print(e, blogger.login, 'error file')
            return '0_0'

        st = time.monotonic()

        print('time', time.monotonic() - st)

        blogger.subscribers_parsed = True
        blogger.save()

    def get_new_blogger(self):
        return Blogger.objects.filter(subscribers_in_process=False).order_by('post_default_count', '-priority').first()
