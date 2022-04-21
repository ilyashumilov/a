from django.db import models


class Status(models.Model):
    original_name = models.CharField(max_length=255)
    native_name = models.CharField(max_length=255, null=True, default=None)

    class Meta:
        db_table = "main_status"
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"

    def __str__(self):
        return self.original_name


class Address(models.Model):
    city_id = models.BigIntegerField(db_index=True, primary_key=True)
    city_name = models.CharField(max_length=255)
    native_city = models.CharField(max_length=255, null=True, default=None)
    native_country = models.CharField(max_length=255, null=True, default=None)

    original_city = models.CharField(max_length=255, null=True, default=None)
    original_country = models.CharField(max_length=255, null=True, default=None)

    latitude_longitude = models.CharField(max_length=100, null=True, default=None)

    auto_checked = models.BooleanField(default=False)

    class Meta:
        db_table = 'main_address'


class Gender(models.Model):
    original_name = models.CharField(max_length=255)
    native_name = models.CharField(max_length=255, null=True, default=None)

    class Meta:
        db_table = 'hype_gender'

    def __str__(self):
        return self.original_name


class VerificationType(models.Model):
    original_name = models.CharField(max_length=255)
    native_name = models.CharField(max_length=255, null=True, default=None)

    class Meta:
        db_table = 'main_verification_type'

    def __str__(self):
        return self.original_name


class Emotion(models.Model):
    original_name = models.CharField(max_length=100)
    native_name = models.CharField(max_length=255, null=True, default=None)

    class Meta:
        db_table = 'hype_emotion'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    original_name = models.CharField(max_length=100, null=True, default=None)
    native_name = models.CharField(max_length=100, null=True, default=None)

    class Meta:
        db_table = 'hype_category'


class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)
    original_name = models.CharField(max_length=50, null=True, default=None)
    native_name = models.CharField(max_length=50, null=True, default=None)

    class Meta:
        db_table = 'hype_language'
