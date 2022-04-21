from django.db import models


class SocialNetwork(models.Model):
    name = models.CharField(max_length=255)
    photo = models.CharField(max_length=255, default=None, null=True)

    class Meta:
        db_table = 'extra_social_network_type'

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)
    native_name = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'extra_city'

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=255)
    native_name = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'extra_country'

    def __str__(self):
        return self.name


class Language(models.Model):
    lang = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'extra_language'

    def __str__(self):
        return self.name


class VerificationType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'extra_verification_type'

    def __str__(self):
        return self.name


class Gender(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'extra_gender'

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "extra_status"
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"

    def __str__(self):
        return self.name
