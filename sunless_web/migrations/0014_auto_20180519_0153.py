# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-18 16:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sunless_web', '0013_auto_20180519_0152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noun',
            name='final',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='최종본'),
        ),
        migrations.AlterField(
            model_name='noun',
            name='google',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='구글'),
        ),
        migrations.AlterField(
            model_name='noun',
            name='name',
            field=models.CharField(max_length=100, verbose_name='이름'),
        ),
        migrations.AlterField(
            model_name='noun',
            name='papago',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='파파고'),
        ),
        migrations.AlterField(
            model_name='noun',
            name='reference',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='참고의견'),
        ),
        migrations.AlterField(
            model_name='noun',
            name='translate',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='번역'),
        ),
    ]
