# Generated by Django 2.0.5 on 2018-05-28 14:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sunless_web', '0030_auto_20180528_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='status',
            field=models.IntegerField(choices=[(0, '안됨'), (1, '진행 중'), (2, '완료')], default=0, verbose_name='번역 상태'),
        ),
    ]
