# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-05-24 16:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('t2f', '0014_auto_20170522_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='publics.Currency'),
        ),
    ]