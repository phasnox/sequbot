# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-08-03 21:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sequbot_data', '0019_auto_20160726_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='instagramtestsubject',
            name='is_follow_source',
            field=models.BooleanField(default=False),
        ),
    ]
