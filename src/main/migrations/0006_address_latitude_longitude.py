# Generated by Django 4.0 on 2022-03-27 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_cachedb_archive'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='latitude_longitude',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
    ]