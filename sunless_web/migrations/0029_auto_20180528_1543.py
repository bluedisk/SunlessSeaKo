# Generated by Django 2.0.5 on 2018-05-28 06:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sunless_web', '0028_auto_20180528_1518'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entity',
            old_name='create_at',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='entity',
            old_name='update_at',
            new_name='updated_at',
        ),
        migrations.RenameField(
            model_name='noun',
            old_name='create_at',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='noun',
            old_name='update_at',
            new_name='updated_at',
        ),
    ]