# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-12-07 14:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tpm', '0007_auto_20171113_1222'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tpmactivity',
            old_name='partnership',
            new_name='intervention',
        ),
        migrations.RenameField(
            model_name='tpmactivity',
            old_name='implementing_partner',
            new_name='partner',
        ),
    ]
