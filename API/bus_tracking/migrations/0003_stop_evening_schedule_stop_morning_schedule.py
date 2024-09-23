# Generated by Django 5.1.1 on 2024-09-22 03:43

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_tracking', '0002_alter_passedstop_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='stop',
            name='evening_schedule',
            field=models.TimeField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stop',
            name='morning_schedule',
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
