from django.db import models

from main.models import Blogger


class BloggerHistory(models.Model):
    blogger = models.ForeignKey(Blogger, on_delete=models.CASCADE, related_name="history")
    followers_count = models.IntegerField()
    following_count = models.IntegerField()
    contents_count = models.IntegerField()
    parsed_date = models.DateTimeField(auto_created=True)


