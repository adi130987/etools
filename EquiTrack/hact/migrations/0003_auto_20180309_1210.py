# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-03-09 12:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hact', '0002_aggregatehact'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='hacthistory',
            options={'verbose_name_plural': 'Hact Histories'},
        ),
    ]