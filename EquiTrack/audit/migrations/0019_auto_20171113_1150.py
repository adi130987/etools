# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-11-13 11:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0018_auto_20171113_1009'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditorfirm',
            name='deleted_flag',
            field=models.BooleanField(default=False, verbose_name='Marked For Deletion in VISION'),
        ),
        migrations.AddField(
            model_name='auditorfirm',
            name='vision_synced',
            field=models.BooleanField(default=False, verbose_name='Synced from VISION'),
        ),
        migrations.AlterField(
            model_name='auditorfirm',
            name='blocked',
            field=models.BooleanField(default=False, verbose_name='Blocked in VISION'),
        ),
    ]
