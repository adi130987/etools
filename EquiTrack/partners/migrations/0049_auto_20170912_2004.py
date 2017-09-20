# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-09-12 20:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0048_auto_20170823_2012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filetype',
            name='name',
            field=models.CharField(choices=[('FACE', 'FACE'), ('Progress Report', 'Progress Report'), ('Partnership Review', 'Partnership Review'), ('Final Partnership Review', 'Final Partnership Review'), ('Correspondence', 'Correspondence'), ('Supply/Distribution Plan', 'Supply/Distribution Plan'), ('Other', 'Other')], max_length=64, unique=True),
        ),
    ]
