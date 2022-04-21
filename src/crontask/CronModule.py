from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger


class CronModule:
    def __init__(self):
        self.scheduler = BlockingScheduler()

    def add_job(self, time: str, func):
        """%H:%M"""
        date_time = datetime.strptime(time, '%H:%M')
        self.scheduler.add_job(func, trigger=CronTrigger(hour=date_time.hour,
                                                         minute=date_time.minute),
                               replace_existing=True)

    def start(self):
        self.scheduler.print_jobs()
        print('scheduler start')
        self.scheduler.start()
