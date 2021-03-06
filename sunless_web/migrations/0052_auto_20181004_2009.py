# Generated by Django 2.0.5 on 2018-10-04 11:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sunless_web', '0051_auto_20181004_1647'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entrypath',
            options={'ordering': ['name'], 'verbose_name': '번역 위치', 'verbose_name_plural': '번역 위치 목록'},
        ),
        migrations.RemoveField(
            model_name='entry',
            name='cate',
        ),
        migrations.AddField(
            model_name='entrypath',
            name='cate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='entries', to='sunless_web.EntityCate', verbose_name='소속 파일'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='path',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='entries',
                                    to='sunless_web.EntryPath'),
        ),
        migrations.AlterField(
            model_name='translation',
            name='text',
            field=models.TextField(blank=True, null=True, verbose_name='번역 제안'),
        ),
    ]
