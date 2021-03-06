# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-17 18:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sequbot_data', '0003_auto_20160414_1458'),
    ]

    operations = [
        migrations.CreateModel(
            name='WordCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('words', models.TextField(blank=True, null=True)),
                ('source', models.CharField(max_length=10)),
                ('extracted', models.DateField()),
            ],
            options={
                'db_table': 'word_count',
            },
        ),
        migrations.RemoveField(
            model_name='features',
            name='social_account',
        ),
        migrations.RenameField(
            model_name='instagramtestsubject',
            old_name='bio_vector',
            new_name='scores',
        ),
        migrations.RenameField(
            model_name='instagramtestsubject',
            old_name='caption_vector',
            new_name='vectors',
        ),
        migrations.RemoveField(
            model_name='instagramtestsubject',
            name='bio_score',
        ),
        migrations.RemoveField(
            model_name='instagramtestsubject',
            name='caption_score',
        ),
        migrations.RemoveField(
            model_name='instagramtestsubject',
            name='counts_vector',
        ),
        migrations.RemoveField(
            model_name='instagramuser',
            name='bio_words',
        ),
        migrations.RemoveField(
            model_name='instagramuser',
            name='caption_words',
        ),
        migrations.AddField(
            model_name='socialaccount',
            name='target_conditions',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='Features',
        ),
        migrations.AddField(
            model_name='wordcount',
            name='social_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sequbot_data.SocialAccount'),
        ),
    ]
