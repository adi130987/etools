# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-12-15 10:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import t2f.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('locations', '0002_auto_20161118_0631'),
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reports', '0002_auto_20161209_2030'),
        ('partners', '0003_auto_20161209_2030'),
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
            name='Clearances',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medical_clearance', models.CharField(choices=[('requested', 'requested'), ('not_requested', 'not_requested'), ('not_applicable', 'not_applicable')], default='not_applicable', max_length=14)),
                ('security_clearance', models.CharField(choices=[('requested', 'requested'), ('not_requested', 'not_requested'), ('not_applicable', 'not_applicable')], default='not_applicable', max_length=14)),
                ('security_course', models.CharField(choices=[('requested', 'requested'), ('not_requested', 'not_requested'), ('not_applicable', 'not_applicable')], default='not_applicable', max_length=14)),
            ],
        ),
        migrations.CreateModel(
            name='CostAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('share', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('iso_4217', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Deduction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('breakfast', models.BooleanField(default=False)),
                ('lunch', models.BooleanField(default=False)),
                ('dinner', models.BooleanField(default=False)),
                ('accomodation', models.BooleanField(default=False)),
                ('no_dsa', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DSARegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('dsa_amount_usd', models.DecimalField(decimal_places=4, max_digits=20)),
                ('dsa_amount_60plus_usd', models.DecimalField(decimal_places=4, max_digits=20)),
                ('dsa_amount_local', models.DecimalField(decimal_places=4, max_digits=20)),
                ('dsa_amount_60plus_local', models.DecimalField(decimal_places=4, max_digits=20)),
                ('room_rate', models.DecimalField(decimal_places=4, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=4, max_digits=10)),
                ('account_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='t2f.Currency')),
                ('document_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='t2f.Currency')),
            ],
        ),
        migrations.CreateModel(
            name='ExpenseType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32)),
                ('code', models.CharField(max_length=16)),
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
            name='IteneraryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origin', models.CharField(max_length=255)),
                ('destination', models.CharField(max_length=255)),
                ('departure_date', models.DateTimeField()),
                ('arrival_date', models.DateTimeField()),
                ('overnight_travel', models.BooleanField(default=False)),
                ('airlines', models.ManyToManyField(related_name='_iteneraryitem_airlines_+', to='t2f.AirlineCompany')),
                ('dsa_region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='t2f.DSARegion')),
            ],
        ),
        migrations.CreateModel(
            name='ModeOfTravel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Plane', 'Plane'), ('Bus', 'Bus'), ('Car', 'Car'), ('Boat', 'Boat'), ('Rail', 'Rail')], max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='Travel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('completed_at', models.DateTimeField(null=True)),
                ('canceled_at', models.DateTimeField(null=True)),
                ('submitted_at', models.DateTimeField(null=True)),
                ('rejected_at', models.DateTimeField(null=True)),
                ('approved_at', models.DateTimeField(null=True)),
                ('rejection_note', models.TextField(null=True)),
                ('cancellation_note', models.TextField(null=True)),
                ('certification_note', models.TextField(null=True)),
                ('report_note', models.TextField(null=True)),
                ('misc_expenses', models.TextField(null=True)),
                ('status', django_fsm.FSMField(choices=[('planned', 'Planned'), ('submitted', 'Submitted'), ('rejected', 'Rejected'), ('approved', 'Approved'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('sent_for_payment', 'Sent for payment'), ('certification_submitted', 'Certification submitted'), ('certification_approved', 'Certification approved'), ('certification_rejected', 'Certification rejected'), ('certified', 'Certified'), ('completed', 'Completed')], default='planned', max_length=50, protected=True)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('purpose', models.CharField(blank=True, max_length=500, null=True)),
                ('additional_note', models.TextField(blank=True, null=True)),
                ('international_travel', models.NullBooleanField(default=False)),
                ('ta_required', models.NullBooleanField(default=True)),
                ('reference_number', models.CharField(default=t2f.models.make_reference_number, max_length=12)),
                ('hidden', models.BooleanField(default=False)),
                ('estimated_travel_cost', models.DecimalField(decimal_places=4, default=0, max_digits=20)),
                ('is_driver', models.BooleanField(default=False)),
                ('preserved_expenses', models.DecimalField(decimal_places=4, default=None, max_digits=20, null=True)),
                ('currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='t2f.Currency')),
                ('mode_of_travel', models.ManyToManyField(related_name='_travel_mode_of_travel_+', to='t2f.ModeOfTravel')),
                ('office', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.Office')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.Section')),
                ('supervisor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('traveler', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='travels', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TravelActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary_traveler', models.BooleanField(default=True)),
                ('date', models.DateTimeField(null=True)),
                ('locations', models.ManyToManyField(related_name='_travelactivity_locations_+', to='locations.Location')),
                ('partner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='partners.PartnerOrganization')),
                ('partnership', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='partners.PCA')),
                ('result', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='reports.Result')),
            ],
        ),
        migrations.CreateModel(
            name='TravelAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=t2f.models.determine_file_upload_path)),
                ('travel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='t2f.Travel')),
            ],
        ),
        migrations.CreateModel(
            name='TravelPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('code', models.CharField(max_length=128)),
                ('status', models.CharField(choices=[('planned', 'Planned'), ('submitted', 'Submitted'), ('rejected', 'Rejected'), ('approved', 'Approved'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('sent_for_payment', 'Sent for payment'), ('certification_submitted', 'Certification submitted'), ('certification_approved', 'Certification approved'), ('certification_rejected', 'Certification rejected'), ('certified', 'Certified'), ('completed', 'Completed')], max_length=50)),
                ('user_type', models.CharField(choices=[('God', 'God'), ('Anyone', 'Anyone'), ('Traveler', 'Traveler'), ('Travel Administrator', 'Travel Administrator'), ('Supervisor', 'Supervisor'), ('Travel Focal Point', 'Travel Focal Point'), ('Finance Focal Point', 'Finance Focal Point'), ('Representative', 'Representative')], max_length=25)),
                ('model', models.CharField(max_length=128)),
                ('field', models.CharField(max_length=64)),
                ('permission_type', models.CharField(choices=[('edit', 'Edit'), ('view', 'View')], max_length=5)),
                ('value', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TravelType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Programmatic Visit', 'Programmatic Visit'), ('Spot Check', 'Spot Check'), ('Advocacy', 'Advocacy'), ('Technical Support', 'Technical Support'), ('Meeting', 'Meeting'), ('Staff Development', 'Staff Development'), ('Staff Entitlement', 'Staff Entitlement')], max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='WBS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
            ],
        ),
        migrations.AddField(
            model_name='travelactivity',
            name='travel_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='t2f.TravelType'),
        ),
        migrations.AddField(
            model_name='travelactivity',
            name='travels',
            field=models.ManyToManyField(related_name='activities', to='t2f.Travel'),
        ),
        migrations.AddField(
            model_name='iteneraryitem',
            name='mode_of_travel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='t2f.ModeOfTravel'),
        ),
        migrations.AddField(
            model_name='iteneraryitem',
            name='travel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itinerary', to='t2f.Travel'),
        ),
        migrations.AddField(
            model_name='grant',
            name='wbs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grants', to='t2f.WBS'),
        ),
        migrations.AddField(
            model_name='fund',
            name='grant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='funds', to='t2f.Grant'),
        ),
        migrations.AddField(
            model_name='expense',
            name='travel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='t2f.Travel'),
        ),
        migrations.AddField(
            model_name='expense',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='t2f.ExpenseType'),
        ),
        migrations.AddField(
            model_name='deduction',
            name='travel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deductions', to='t2f.Travel'),
        ),
        migrations.AddField(
            model_name='costassignment',
            name='fund',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='t2f.Fund'),
        ),
        migrations.AddField(
            model_name='costassignment',
            name='grant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='t2f.Grant'),
        ),
        migrations.AddField(
            model_name='costassignment',
            name='travel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cost_assignments', to='t2f.Travel'),
        ),
        migrations.AddField(
            model_name='costassignment',
            name='wbs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='t2f.WBS'),
        ),
        migrations.AddField(
            model_name='clearances',
            name='travel',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='clearances', to='t2f.Travel'),
        ),
    ]