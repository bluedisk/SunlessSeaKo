# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-13 14:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sunless_web', '0006_auto_20180513_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='parent',
            field=models.CharField(blank=True, max_length=70, null=True, verbose_name='Parent Entity Name'),
        ),
    ]
