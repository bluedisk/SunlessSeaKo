# Generated by Django 2.1.2 on 2018-10-25 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sunless_web', '0059_auto_20181025_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discussion',
            name='translate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discuss', to='sunless_web.Translation'),
        ),
    ]