# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-20 13:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_post_likes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='likes',
            field=models.ManyToManyField(blank=True, null=True, related_name='liked', to=settings.AUTH_USER_MODEL),
        ),
    ]
