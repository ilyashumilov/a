# Generated by Django 4.0 on 2022-04-05 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brand_parser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='native_name',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='brand',
            name='original_name',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
