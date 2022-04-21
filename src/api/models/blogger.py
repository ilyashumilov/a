from django.contrib.postgres.fields import ArrayField
from django.db import models

from .base import BaseModel
from .extra import SocialNetwork, VerificationType, Country, City, Gender, Status
from ..extra import create_photo_link

args = dict(db_index=True, null=True, blank=True)


class ProceedBlogger(BaseModel):
    login = models.CharField(max_length=255, db_index=True, blank=True)
    social_id = models.CharField(max_length=255, null=True, default=None, db_index=True, blank=True)
    social_network_type = models.ForeignKey(SocialNetwork, on_delete=models.DO_NOTHING, db_index=True, blank=True)

    # count
    subscribers_count = models.BigIntegerField(default=None, null=True, db_index=True, blank=True)
    contents_count = models.BigIntegerField(default=None, null=True, db_index=True, blank=True)
    following = models.BigIntegerField(default=None, null=True, db_index=True, blank=True)
    default_total = models.BigIntegerField(default=None, null=True, blank=True)

    # info
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, default=None)
    verification_type = models.ForeignKey(VerificationType, on_delete=models.SET_NULL, **args)
    categories = ArrayField(models.IntegerField(), default=None, null=True, db_index=True, blank=True)
    bio = models.TextField(default=None, null=True, blank=True)
    external_link = models.TextField(default=None, null=True)
    account_creation_date = models.DateField(default=None, null=True, blank=True)

    # extra info
    city = models.ForeignKey(City, on_delete=models.SET_NULL, **args)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, **args)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, **args)
    age = models.IntegerField(default=None, **args)
    phone = models.CharField(max_length=255, default=None, null=True, blank=True)
    email = models.CharField(max_length=255, default=None, null=True, blank=True)
    avatar = models.CharField(max_length=255, default=None, null=True)

    # proceed data
    engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, **args)

    # socials
    name = models.CharField(max_length=255, default=None, null=True)

    # work info
    file_from_info = models.CharField(max_length=55, default=None, null=True)

    open_fields = ['id', 'login', 'social_network_type_id', 'subscribers_count', 'contents_count',
                   'categories', 'city', 'verification_type', 'country', 'gender',
                   'age', 'engagement_rate']

    @property
    def avatar_link(self):
        return create_photo_link(self.avatar)

    class Meta:
        db_table = 'proceed_blogger'
        unique_together = ('login', 'social_network_type_id')
