# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-19 03:24
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sequbot_data', '0017_auto_20160624_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialaccount',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 7, 19, 3, 24, 49, 236393, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
