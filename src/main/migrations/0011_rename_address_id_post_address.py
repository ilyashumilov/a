# Generated by Django 4.0 on 2022-04-15 18:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_bloggerhistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='address_id',
            new_name='address',
        ),
    ]
