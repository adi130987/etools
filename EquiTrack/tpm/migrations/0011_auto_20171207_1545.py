# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-12-07 15:45
from __future__ import unicode_literals

import django
from django.db import migrations, models


def create_activities(apps, schema_editor):
    TPMActivity = apps.get_model('tpm', 'TPMActivity')
    Activity = apps.get_model('activities', 'Activity')

    for tpm_activity in TPMActivity.objects.all():
        activity = Activity.objects.create(
            id=tpm_activity.id,
            cp_output=tpm_activity.cp_output1,
            date=tpm_activity.date1,
            intervention=tpm_activity.intervention1,
            partner=tpm_activity.partner1,
        )

        activity.locations.add(*tpm_activity.locations1.all())


class Migration(migrations.Migration):

    dependencies = [
        ('tpm', '0010_auto_20171207_1513'),
        ('activities', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_activities, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='tpmactivity',
            name='id',
        ),
        migrations.AlterField(
            model_name='tpmactivity',
            name='activity_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='activities.Activity'),
        ),
    ]
