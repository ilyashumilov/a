from django.db.models import QuerySet

from api.models import ProceedBlogger
from api.services.methods import posts_by_day
from brightdata.models import ScrappingPostInfo
from main.models import Post, Blogger


class GraphMethods:
    def __init__(self, post_query, blogger, subscribers):
        self.post_query: QuerySet[Post] = post_query
        self.blogger: ProceedBlogger = blogger
        self.simple_blogger = Blogger.objects.get(id=blogger.id)
        self.proceed_subscribers = subscribers

        self.functions = {

        }

    def frequency_of_publications(self, start, end):
        data = {}

        for post in self.post_query:
            posts_by_day(post, data, start, end)

        data['total_count'] = len(self.post_query)

        return data

    def post_typology(self):
        data = {}

        bright_scrapping_posts = ScrappingPostInfo.objects.filter(blogger_id=self.simple_blogger)
        for bright_post in bright_scrapping_posts:
            for post in self.post_query:
                if post.post_id in bright_post.short_code:
                    t_date = f"{post.date.day}.{post.date.month}.{post.date.year}"
                    data[t_date] = {'feed': 0, 'image': 0, 'sidecar': 0, 'igtv': 0}
                    data[t_date][bright_post.type_of_post] += 1

        return data


