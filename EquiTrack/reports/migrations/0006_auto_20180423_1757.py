# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-04-23 17:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_reportingrequirement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appliedindicator',
            name='means_of_verification',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Means of Verification'),
        ),
    ]
