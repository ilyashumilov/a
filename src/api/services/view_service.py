import json
import sys
import time
import traceback

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework.response import Response

from main.models import Archive
from api.services.api_service import StatisticMethods
from main.models import Post, Subscriber, Blogger
from parsing.AsyncParsingNew.utils import time_print


def base_data(blogger_login: str):
    # blogger: ProceedBlogger = get_object_or_404(ProceedBlogger, login=blogger_login, social_network_type_id=3)
    blogger = Blogger.objects.get_default(login=blogger_login)
    post_query = Post.objects.filter(blogger_id=blogger.id, is_deleted=False).order_by('-date')
    st = time.monotonic()
    subscribers = Subscriber.objects.filter(Q(bloggers__overlap=[blogger.id]) & Q(following__gte=0))
    return blogger, post_query, subscribers, blogger


def data_create_not_exists(data: dict, blogger: Blogger, parsing_task_blogger=None):
    if data == {} or data is None:
        return

    Archive.objects.get_or_create(blogger_id=blogger.id, parsing_task_blogger=parsing_task_blogger,
                                  day=timezone.now().date(),
                                  defaults={'data': json.dumps(data, ensure_ascii=False)}
                                  )


def get_statistic(blogger_login):
    try:
        if settings.IS_ARCHIVE_ACTIVE:
            archive = Archive.objects.filter(blogger__login=blogger_login).order_by('-day').first()
            if archive is not None:
                time_print('archive worked', blogger_login)
                blg = Blogger.objects.get(login=blogger_login, social_network_type_id=3)
                result = dict(json.loads(archive.data))
                result['parsing']['refreshing'] = blg.parsing_measurement

                return Response(result)
        blogger, post_query, subscribers, blogger_simple = base_data(blogger_login)

        sm = StatisticMethods(post_query=post_query, blogger=blogger, subscribers=subscribers,
                              blogger_simple=blogger_simple)
        data = sm.all_by_one_cycle()
        if settings.IS_ARCHIVE_ACTIVE:
            data_create_not_exists(data, blogger)
        return Response(data)
    except Exception as e:
        time_print('ERROR', f"login: {blogger_login}", e,
                   ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e))
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        print(tbinfo)

        return Response({'error': str(e)})
