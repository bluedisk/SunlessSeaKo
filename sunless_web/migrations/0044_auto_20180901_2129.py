# Generated by Django 2.0.5 on 2018-09-01 12:29

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('sunless_web', '0043_auto_20180901_2121'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entry',
            old_name='text_jr',
            new_name='text_jp',
        ),
        migrations.RenameField(
            model_name='entry',
            old_name='text_jrkr',
            new_name='text_jpkr',
        ),
    ]
