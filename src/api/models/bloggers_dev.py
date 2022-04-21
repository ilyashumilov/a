from django.db import models


class TiktokBloggers(models.Model):
    # db_column
    id = models.BigAutoField(primary_key=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=3000, blank=True, null=True)
    updated_at = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    followers = models.IntegerField(blank=True, null=True)
    friends = models.IntegerField(blank=True, null=True)
    likes = models.CharField(max_length=255, blank=True, null=True)
    diggs = models.IntegerField(blank=True, null=True)
    publications = models.IntegerField(blank=True, null=True)
    is_verify = models.IntegerField(blank=True, null=True)
    avg_views_per_video = models.IntegerField(blank=True, null=True)
    avg_comments_per_video = models.IntegerField(blank=True, null=True)
    avg_duration_per_video = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    instagram = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        app_label = 'bloggers_dev'
        db_table = 'tiktok_bloggers'


class YoutubeBloggers(models.Model):
    id = models.BigAutoField(primary_key=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=3000, blank=True, null=True)
    followers = models.IntegerField(blank=True, null=True)
    downloads = models.IntegerField(blank=True, null=True)
    updated_at = models.CharField(max_length=255, blank=True, null=True)
    all_views = models.CharField(max_length=255, blank=True, null=True)
    likes_for_5_videos = models.CharField(max_length=255, blank=True, null=True)
    dislikes_for_5_videos = models.IntegerField(blank=True, null=True)
    avg_views = models.IntegerField(blank=True, null=True)
    channel_theme = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        app_label = 'bloggers_dev'
        db_table = 'youtube_bloggers'
