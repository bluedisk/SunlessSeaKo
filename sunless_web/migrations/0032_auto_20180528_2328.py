# Generated by Django 2.0.5 on 2018-05-28 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sunless_web', '0031_entity_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='status',
            field=models.CharField(choices=[('none', '안됨'), ('in', '진행 중'), ('done', '완료')], default='none', max_length=4, verbose_name='번역 상태'),
        ),
    ]
