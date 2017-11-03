# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-10-27 14:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0017_auto_20171026_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appliedindicator',
            name='baseline',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Baseline'),
        ),
        migrations.AlterField(
            model_name='appliedindicator',
            name='cluster_indicator_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Cluster Indicator ID'),
        ),
        migrations.AlterField(
            model_name='appliedindicator',
            name='cluster_indicator_title',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='Cluster Indicator Title'),
        ),
        migrations.AlterField(
            model_name='appliedindicator',
            name='disaggregation',
            field=models.ManyToManyField(blank=True, related_name='applied_indicators', to='reports.Disaggregation', verbose_name='Disaggregation Logic'),
        ),
        migrations.AlterField(
            model_name='appliedindicator',
            name='indicator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reports.IndicatorBlueprint', verbose_name='Indicator'),
        ),
        migrations.AlterField(
            model_name='appliedindicator',
            name='locations',
            field=models.ManyToManyField(related_name='applied_indicators', to='locations.Location', verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='appliedindicator',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reports.Sector', verbose_name='Section'),
        ),
        migrations.AlterField(
            model_name='appliedindicator',
            name='target',
            field=models.PositiveIntegerField(default=0, verbose_name='Target'),
        ),
        migrations.AlterField(
            model_name='indicatorblueprint',
            name='calculation_formula_across_locations',
            field=models.CharField(choices=[('sum', 'sum'), ('max', 'max'), ('avg', 'avg'), ('percentage', 'percentage'), ('ratio', 'ratio')], default='sum', max_length=10, verbose_name='Calculation Formula across Locations'),
        ),
        migrations.AlterField(
            model_name='indicatorblueprint',
            name='calculation_formula_across_periods',
            field=models.CharField(choices=[('sum', 'sum'), ('max', 'max'), ('avg', 'avg'), ('percentage', 'percentage'), ('ratio', 'ratio')], default='sum', max_length=10, verbose_name='Calculation Formula across Periods'),
        ),
        migrations.AlterField(
            model_name='indicatorblueprint',
            name='display_type',
            field=models.CharField(choices=[('number', 'number'), ('percentage', 'percentage'), ('ratio', 'ratio')], default='number', max_length=10, verbose_name='Display Type'),
        ),
        migrations.AlterField(
            model_name='indicatorblueprint',
            name='unit',
            field=models.CharField(choices=[('number', 'number'), ('percentage', 'percentage')], default='number', max_length=10, verbose_name='Unit'),
        ),
    ]