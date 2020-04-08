# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-14 14:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sequbot_data', '0002_socialaccount_work_days'),
    ]

    operations = [
        migrations.AlterField(
            model_name='features',
            name='bio_features',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='features',
            name='caption_features',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='instagramtestsubject',
            name='bio_vector',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='instagramtestsubject',
            name='caption_vector',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='instagramtestsubject',
            name='counts_vector',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='instagramuser',
            name='bio_words',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='instagramuser',
            name='caption_words',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='instagramuser',
            name='raw_data',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='socialaccount',
            name='ai_params',
            field=models.TextField(blank=True, null=True),
        ),
    ]
