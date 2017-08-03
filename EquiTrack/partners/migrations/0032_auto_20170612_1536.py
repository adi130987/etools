# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-06-12 15:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0031_planned_budget_consolidation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interventionbudget',
            name='intervention',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='planned_budget', to='partners.Intervention'),
        ),
        migrations.AlterUniqueTogether(
            name='interventionbudget',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='interventionbudget',
            name='year',
        ),
    ]
