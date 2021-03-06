# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-13 11:31
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nid', models.IntegerField(db_index=True, verbose_name='node Id')),
                ('parent', models.CharField(db_index=True, max_length=32, verbose_name='Parent Entity Name')),
                ('hash', models.CharField(db_index=True, max_length=32, verbose_name='HashHex')),
                ('original', models.TextField(blank=True, null=True, verbose_name='Original Text(JSON)')),
                ('reference', models.TextField(blank=True, null=True, verbose_name='Reference Text(JSON)')),
                ('google', models.TextField(blank=True, null=True, verbose_name='Google Translated Text(JSON)')),
                ('papago', models.TextField(blank=True, null=True, verbose_name='Papago Translated Text(JSON)')),
                ('translate', models.TextField(blank=True, null=True, verbose_name='Translated Text(JSON)')),
                ('final', models.TextField(blank=True, null=True, verbose_name='Final Text(JSON)')),
            ],
        ),
        migrations.CreateModel(
            name='EntityFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='entity',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entities',
                                    to='sunless_web.EntityFile'),
        ),
    ]
