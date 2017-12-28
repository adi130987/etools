# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-12-18 18:59
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('partners', '0054_auto_20171013_2147'),
    ]

    operations = [
        migrations.CreateModel(
            name='HactHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('year', models.IntegerField(default=2017)),
                ('partner_values', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_partner', to='partners.PartnerOrganization')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='hacthistory',
            unique_together=set([('partner', 'year')]),
        ),
    ]