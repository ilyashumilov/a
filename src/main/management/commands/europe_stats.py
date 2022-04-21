from django.core.management import BaseCommand

# europe_stats
from main.models import Blogger, Post, Subscriber, Comment, Like
from parsing.AsyncParsingNew.utils import chunks


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


countries = ["Испания", "Индонезия", "Польша", "Италия", "Вьетнам", "Узбекистан",
             "Азербайджан", "Германия", "Португалия", "Тайланд", "Англия"]



def worker():
    for country in countries:
        print(country)
        bloggers = Blogger.objects.filter(social_network_type_id=3, file_from_info__overlap=[country])
        bloggers_ids = [i.id for i in bloggers]
        print("bloggers", len(bloggers_ids))

        posts = list(Post.objects.filter(blogger_id__in=bloggers_ids).values_list('id', flat=True))
        print("posts", len(posts))

        subscribers = 0
        for mini in chunks(bloggers_ids, 100):
            subscribers += Subscriber.objects.filter(bloggers__overlap=mini).count()
        print("subscribers", subscribers)

        comments = Comment.objects.filter(post_id__in=posts).count()
        print("comments", comments)

        likes = Like.objects.filter(post_id__in=posts).count()
        print("likes", likes)

        print('----------')
