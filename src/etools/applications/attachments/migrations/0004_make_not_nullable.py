# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-02-19 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0003_fix_null_values'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='hyperlink',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Hyperlink'),
        ),
    ]
