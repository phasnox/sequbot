# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-10 00:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sequbot_data', '0011_auto_20160505_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='instagramsource',
            name='username',
            field=models.CharField(default='username', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='socialaccount',
            name='social_site_id',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='socialaccount',
            name='stats_updated',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.RemoveField(
            model_name='socialaccount',
            name='cookies',
        ),
        migrations.AlterUniqueTogether(
            name='socialaccount',
            unique_together=set([('username', 'social_site')]),
        ),
    ]
