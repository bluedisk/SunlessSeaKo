# Generated by Django 2.1.2 on 2018-10-25 13:18

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sunless_web', '0055_auto_20181025_2216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='final',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Final Text(JSON)'),
        ),
        migrations.AlterField(
            model_name='entity',
            name='google',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Google Translated Text(JSON)'),
        ),
        migrations.AlterField(
            model_name='entity',
            name='marked',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Noun marked Original Text(JSON)'),
        ),
        migrations.AlterField(
            model_name='entity',
            name='original',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Original Text(JSON)'),
        ),
        migrations.AlterField(
            model_name='entity',
            name='papago',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Papago Translated Text(JSON)'),
        ),
        migrations.AlterField(
            model_name='entity',
            name='reference',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Reference Text(JSON)'),
        ),
        migrations.AlterField(
            model_name='entity',
            name='translate',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Translated Text(JSON)'),
        ),
    ]
