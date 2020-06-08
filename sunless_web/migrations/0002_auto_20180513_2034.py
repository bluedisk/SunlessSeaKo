# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-13 11:34
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sunless_web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='create_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now,
                                       verbose_name='created time'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entity',
            name='update_at',
            field=models.DateTimeField(auto_now=True, verbose_name='updated time'),
        ),
    ]
