# Generated by Django 2.0.5 on 2018-09-01 12:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sunless_web', '0041_auto_20180901_2058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='cate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='entries', to='sunless_web.EntityCate', verbose_name='소속 파일'),
        ),
    ]
