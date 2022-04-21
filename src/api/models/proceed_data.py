from django.contrib.postgres.fields import JSONField, ArrayField
from djchoices import DjangoChoices, ChoiceItem

from api.models.base import BaseModel
from django.db import models


class Quality(models.Model):
    # the_most_high = ChoiceItem("Очень высокое", "81-100")
    # high = ChoiceItem("Высокое", '61-80')
    # middle = ChoiceItem("Среднее", '41-60')
    # bad = ChoiceItem('Плохое', '21-40')
    # the_baddest = ChoiceItem('Очень плохое', '0-20')
    name = models.CharField(max_length=50)
    maximum = models.SmallIntegerField()
    minimum = models.SmallIntegerField()

    class Meta:
        db_table = 'extra_quality'


# class AudienceType(DjangoChoices):
#     normal = ChoiceItem('Качественная аудитория')
#     suspect = ChoiceItem("Подозрительные аккаунты")
#     mass_followers = ChoiceItem("Массфоловеры")
#     loms = ChoiceItem("Лидеры мнений")


class SubscribersDataForBlogger(BaseModel):
    audience_quality = models.ForeignKey(Quality, on_delete=models.SET_NULL)
    type_of_audience = JSONField()
    gender_and_age = JSONField()


class BloggerAnotherSocial(BaseModel):
    blogger_id = models.BigIntegerField(db_index=True)
    bloggers = ArrayField(models.BigIntegerField(), default=list, null=True, blank=True)
    social_network = models.ForeignKey('api.SocialNetwork', on_delete=models.DO_NOTHING)
    social_network_url = models.CharField(max_length=255, default=None, null=True)

    class Meta:
        db_table = 'blogger_another_social'
