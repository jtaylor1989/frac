# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-16 14:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20171112_2139'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
