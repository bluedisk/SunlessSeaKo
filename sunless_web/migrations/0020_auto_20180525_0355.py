# Generated by Django 2.0.5 on 2018-05-24 18:55

import django.contrib.postgres.fields.jsonb
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sunless_web', '0019_auto_20180520_1730'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entity',
            name='noun_error',
        ),
        migrations.AddField(
            model_name='entity',
            name='error',
            field=models.TextField(null=True, verbose_name='error'),
        ),
        migrations.AddField(
            model_name='entity',
            name='marked',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={},
                                                                 verbose_name='Noun marked Original Text(JSON)'),
        ),
        migrations.AlterField(
            model_name='entity',
            name='checker',
            field=models.ManyToManyField(related_name='entities', to=settings.AUTH_USER_MODEL),
        ),
    ]
