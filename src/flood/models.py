import enum

from django.db import models

# Create your models here.
from djchoices import DjangoChoices, ChoiceItem


class ParsingTaskTypeName(enum.Enum):
    profile_info = 4
    subscribers = 7
    posts = 6
    comments = 3
    filtering = 8
    blogger_filtering = 9
    subscribers_not_detail = 5
    likes = 1


class ParsingTaskBloggerStatus(DjangoChoices):
    not_started = ChoiceItem("not started")
    in_process = ChoiceItem("in process")
    in_transaction = ChoiceItem('in transaction')
    done = ChoiceItem("done")
    error = ChoiceItem("error")


class ParsingTaskBloggerType(DjangoChoices):
    week = ChoiceItem('WEEK')
    one_time = ChoiceItem('ONE_TIME')


class ParsingTaskBlogger(models.Model):
    blogger = models.ForeignKey('main.Blogger', on_delete=models.CASCADE, null=True)
    percent = models.SmallIntegerField(default=0)
    status = models.CharField(choices=ParsingTaskBloggerStatus.choices, max_length=25)
    task_type = models.CharField(choices=ParsingTaskBloggerType.choices, max_length=25)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    day = models.DateField(auto_now_add=True)

    def get_blogger_login(self):
        try:
            return self.blogger.login
        except:
            return None

    class Meta:
        unique_together = ['blogger_id', 'day']
        db_table = 'main_instagram_parsing_task_blogger'


class ParsingTaskMicroservice(models.Model):
    task_blogger = models.ForeignKey(ParsingTaskBlogger, on_delete=models.CASCADE)
    status = models.CharField(choices=ParsingTaskBloggerStatus.choices, max_length=25, db_index=True)
    parser_task_id = models.BigIntegerField(default=None, null=True, db_index=True)
    task_type_id = models.SmallIntegerField()
    task_type_name = models.CharField(max_length=25)

    extra_info = models.JSONField(default=None, null=True)
    data = models.JSONField(default=None, null=True)

    progress = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_blogger_login(self):
        try:
            return self.task_blogger.blogger.login
        except:
            return None

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'main_instagram_parsing_task_microservice'
