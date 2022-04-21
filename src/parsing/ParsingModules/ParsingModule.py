import time
from datetime import datetime
from typing import List

import requests
from django.db.models import Q
from tqdm import tqdm

from main.enum import MethodEnum
from main.models import Blogger


def time_print(*args):
    print(*args, 'time:', datetime.now().strftime('%H:%M %d.%m'))


def download(tid: int, parser):
    while True:
        try:
            url = f'{parser.base_url}api.php?key={parser.api_key}&mode=result&tid={tid}'
            response = requests.get(url.format(tid))
            response.encoding = 'utf-8'
            return response
        except Exception as e:
            print(e, 'sleep')
            time.sleep(60)


class ParsingModule(object):
    parsing_method: int
    task_prefix: str

    def get_task_prefix(self):
        return f"{self.task_prefix}: "

    # override

    def create_dict(self, blogger_login, parse) -> dict:
        pass

    def change_blogger_state(self, blogger: Blogger):
        pass

    def check_parsed(self, blogger: Blogger):
        pass

    def push_to_db(self, response: requests.Response, blogger: Blogger):
        pass

    def get_new_blogger(self):
        pass

    # done

    def get_parsers(self):
        return
    #     return AccountParser.objects.filter(account_type=self.parsing_method).order_by('id')

    def automate_create_task(self):
        while True:
            blogger = self.get_new_blogger()
            print(blogger.login)
            if blogger is None:
                time.sleep(60)
                continue
            while True:
                try:
                    result = self.start_task(blogger)
                    if result is False:
                        time.sleep(60)
                        continue
                    self.change_blogger_state(blogger)
                    break
                except Exception as e:
                    print(e)
                    continue

    def done_tasks(self):

        parsers = self.get_parsers()
        for parser in parsers:
            url = f'{parser.base_url}api.php?key={parser.api_key}&mode=status&status=3'
            time_print('started', url)
            response = requests.get(url).json()
            if 'tasks' not in response:
                continue
            tasks = []
            check_tids = []
            for task in response['tasks']:
                tid: int = task['tid']
                name: str = task['name']
                if not name.startswith(self.task_prefix):
                    continue
                name = name.replace(self.get_task_prefix(), '', 1).strip()
                tasks.append((tid, name))
                check_tids.append(tid)
            # tid_exclude = set(list(TidDone.objects.filter(tid__in=check_tids).values_list('tid', flat=True)))
            tid_exclude=[]
            new_tasks = []
            for task in tasks:
                if task[0] in tid_exclude:
                    continue
                new_tasks.append(task)

            new_tasks.sort(key=lambda x: x[0], reverse=True)
            size = len(tasks)
            time_print(size, 'to download')
            with tqdm(total=size) as pbar:
                for tid, name in tasks:
                    blogger = Blogger.objects.get(login=name)
                    pbar.update(1)
                    while True:
                        result = self.push_to_db(download(tid, parser), blogger)
                        if result == '0_0':
                            time.sleep(60)
                            time_print('download blogger', blogger.login, 'tid', tid, 'again')
                            continue
                        else:
                            break
                    # TidDone.objects.get_or_create(tid=tid)

    def start_task(self, blogger: Blogger):
        parsers = self.get_parsers()
        print(self.task_prefix, self.parsing_method)
        for parser in parsers:
            url = f'{parser.base_url}get/start_task.php'
            dct = self.create_dict(blogger.login, parser)
            headers = {
                'cookie': parser.cookie,
                'user-agent': parser.user_agent
            }
            r = requests.post(headers=headers,
                              data=dct, url=url)
            # print(r.request.body)
            print(r.text)
            if 'limit' not in r.text and 'Forbidden' not in r.text:
                time_print(f"{blogger.login} good")
                parser.bloggers_in_parsing += 1
                parser.save()
                return True
            else:
                time_print(r.text)
                continue
        return False
