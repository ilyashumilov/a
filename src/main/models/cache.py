from django.db import models


class Archive(models.Model):
    blogger = models.ForeignKey('main.Blogger', on_delete=models.CASCADE, db_index=True)
    data = models.TextField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    day = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'hype_bloggers_archive'
        unique_together = ['blogger_id', 'day']


class CacheDB(models.Model):
    blogger = models.ForeignKey('main.Blogger', on_delete=models.DO_NOTHING, db_index=True)
    func_name = models.CharField(max_length=255, db_index=True)
    data = models.JSONField(default=None, null=True)
    day = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hype_rest_cache_db'
