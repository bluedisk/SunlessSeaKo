# Generated by Django 2.0.5 on 2018-10-04 07:47

from django.db import migrations, models
import django.db.models.deletion


def forwards_func(apps, schema_editor):
    Entry = apps.get_model("sunless_web", "Entry")
    EntryPath = apps.get_model("sunless_web", "EntryPath")

    for e in Entry.objects.all():
        ep, _ = EntryPath.objects.get_or_create(name=e.basepath)
        e.path = ep
        e.save()


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('sunless_web', '0050_remove_entry_path'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntryPath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=256, verbose_name='위치')),
            ],
            options={
                'verbose_name': '번역 대상',
                'verbose_name_plural': '번역 대상 목록',
            },
        ),
        migrations.AddField(
            model_name='entry',
            name='path',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sunless_web.EntryPath'),
        ),
        migrations.RunPython(forwards_func, reverse_func)
    ]