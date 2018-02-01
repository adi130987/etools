# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-10-19 12:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('funds', '0005_auto_20170912_2129'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grant',
            options={'ordering': ['donor', 'name', 'description', 'expiry']},
        ),
        migrations.AlterField(
            model_name='grant',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='grant',
            name='donor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='funds.Donor', verbose_name='Donor'),
        ),
        migrations.AlterField(
            model_name='grant',
            name='expiry',
            field=models.DateField(blank=True, null=True, verbose_name='Expiry'),
        ),
        migrations.AlterField(
            model_name='grant',
            name='name',
            field=models.CharField(max_length=128, unique=True, verbose_name='Name'),
        ),
    ]