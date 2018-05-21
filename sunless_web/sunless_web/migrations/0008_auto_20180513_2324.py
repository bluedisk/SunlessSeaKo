# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-13 14:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sunless_web', '0007_auto_20180513_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='hash',
            field=models.CharField(db_index=True, max_length=70, unique=True, verbose_name='HashHex'),
        ),
    ]