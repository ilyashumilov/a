import functools
import json
import time

from django.conf import settings
from django.utils import timezone

from main.models import Archive
from main.models import Blogger
from main.models import CacheDB
from parsing.AsyncParsingNew.utils import time_print


def archive_statistic(func):
    def wrapper(blogger: Blogger, *args):
        day = timezone.now().date()
        data = func(blogger, *args)

        data_json = json.dumps(data, ensure_ascii=False)
        Archive.objects.get_or_create(blogger_id=blogger.id,
                                      day=day,
                                      defaults={'data': data_json}
                                      )
        return data

    return wrapper


def local_pc_check(func):
    def wrapper(*args, **kwargs):
        if not settings.LOCAL_PC:
            return func(*args, **kwargs)
        else:
            return {}

    return wrapper


def cacheable_db_data(func):
    def wrapper(self, *args, **kwargs):
        blogger = self.blogger
        func_name = func.__name__ + f" {self.language}"
        today = timezone.now().date()
        try:

            obj, created = CacheDB.objects.get_or_create(blogger=blogger, func_name=func_name, day=today)
            if created:
                data = func(self, *args, **kwargs)
                obj.data = data
                obj.save(update_fields=['data'])
            else:
                data = obj.data
            return data
        except Exception as e:
            print(e)
            try:
                CacheDB.objects.get(blogger=blogger, func_name=func_name, day=today).delete()
            except:
                pass
            return func(self, *args, **kwargs)

    return wrapper


def timeit(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        elapsed_time = round(time.monotonic() - start_time, 3)
        name = func.__name__

        time_print(name, 'time:', elapsed_time)

        return result

    return new_func
