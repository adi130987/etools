# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-02-02 21:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AirlineCompany',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.IntegerField()),
                ('iata', models.CharField(max_length=3)),
                ('icao', models.CharField(max_length=3)),
                ('country', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='BusinessArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('code', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='BusinessRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('code', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('long_name', models.CharField(max_length=128)),
                ('vision_code', models.CharField(max_length=3, null=True, unique=True)),
                ('iso_2', models.CharField(max_length=2, null=True)),
                ('iso_3', models.CharField(max_length=3, null=True)),
                ('valid_from', models.DateField(null=True)),
                ('valid_to', models.DateField(null=True)),
                ('business_area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='countries', to='publics.BusinessArea')),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('code', models.CharField(max_length=5)),
                ('decimal_places', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='DSARegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_name', models.CharField(max_length=120)),
                ('area_code', models.CharField(max_length=3)),
                ('dsa_amount_usd', models.DecimalField(decimal_places=4, max_digits=20)),
                ('dsa_amount_60plus_usd', models.DecimalField(decimal_places=4, max_digits=20)),
                ('dsa_amount_local', models.DecimalField(decimal_places=4, max_digits=20)),
                ('dsa_amount_60plus_local', models.DecimalField(decimal_places=4, max_digits=20)),
                ('room_rate', models.DecimalField(decimal_places=4, max_digits=20)),
                ('finalization_date', models.DateField()),
                ('eff_date', models.DateField()),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dsa_regions', to='publics.Country')),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField()),
                ('x_rate', models.DecimalField(decimal_places=5, max_digits=10)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchange_rates', to='publics.Currency')),
            ],
        ),
        migrations.CreateModel(
            name='Fund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='TravelAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('code', models.CharField(max_length=12)),
                ('city', models.CharField(max_length=128, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publics.Country')),
            ],
        ),
        migrations.CreateModel(
            name='TravelExpenseType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32)),
                ('vendor_number', models.CharField(max_length=32)),
                ('is_travel_agent', models.BooleanField(default=False)),
                ('rank', models.PositiveIntegerField(default=100)),
            ],
            options={
                'ordering': ('rank', 'title'),
            },
        ),
        migrations.CreateModel(
            name='WBS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('business_area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='publics.BusinessArea')),
            ],
        ),
        migrations.AddField(
            model_name='grant',
            name='wbs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grants', to='publics.WBS'),
        ),
        migrations.AddField(
            model_name='fund',
            name='grant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='funds', to='publics.Grant'),
        ),
        migrations.AddField(
            model_name='country',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='publics.Currency'),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_areas', to='publics.BusinessRegion'),
        ),
    ]
