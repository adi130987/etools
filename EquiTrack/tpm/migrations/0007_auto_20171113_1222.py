# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-11-13 12:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('tpm', '0006_auto_20171019_1215'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tpmpartner',
            options={'verbose_name': 'Organization', 'verbose_name_plural': 'Organizations'},
        ),
        migrations.AlterModelOptions(
            name='tpmpartnerstaffmember',
            options={'verbose_name': 'Staff Member', 'verbose_name_plural': 'Staff Members'},
        ),
        migrations.AlterField(
            model_name='tpmpartner',
            name='blocked',
            field=models.BooleanField(default=False, verbose_name='Blocked in VISION'),
        ),
        migrations.AlterField(
            model_name='tpmpartner',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='tpmpartner',
            name='country',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='tpmpartner',
            name='deleted_flag',
            field=models.BooleanField(default=False, verbose_name='Marked For Deletion in VISION'),
        ),
        migrations.AlterField(
            model_name='tpmpartner',
            name='email',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='tpmpartner',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Hidden'),
        ),
        migrations.AlterField(
            model_name='tpmpartner',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Vendor Name'),
        ),
        migrations.AlterField(
            model_name='tpmpartner',
            name='phone_number',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='tpmpartner',
            name='postal_code',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Postal Code'),
        ),
        migrations.AlterField(
            model_name='tpmpartner',
            name='street_address',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='tpmpartner',
            name='vendor_number',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='Vendor Number'),
        ),
        migrations.AlterField(
            model_name='tpmpartner',
            name='vision_synced',
            field=models.BooleanField(default=False, verbose_name='Synced from VISION'),
        ),
        migrations.AlterField(
            model_name='tpmpartnerstaffmember',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tpm_tpmpartnerstaffmember', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),migrations.AlterField(
            model_name='tpmactionpoint',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_tpm_action_points', to=settings.AUTH_USER_MODEL, verbose_name='Assigned By'),
        ),
        migrations.AlterField(
            model_name='tpmactionpoint',
            name='comments',
            field=models.TextField(blank=True, verbose_name='Comments'),
        ),
        migrations.AlterField(
            model_name='tpmactionpoint',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='tpmactionpoint',
            name='due_date',
            field=models.DateField(verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='tpmactionpoint',
            name='person_responsible',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tpm_action_points', to=settings.AUTH_USER_MODEL, verbose_name='Person Responsible'),
        ),
        migrations.AlterField(
            model_name='tpmactionpoint',
            name='tpm_visit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_points', to='tpm.TPMVisit', verbose_name='Visit'),
        ),
        migrations.AlterField(
            model_name='tpmactivity',
            name='is_pv',
            field=models.BooleanField(default=False, verbose_name='HACT Programmatic Visit'),
        ),
        migrations.AlterField(
            model_name='tpmactivity',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tpm_activities', to='users.Section', verbose_name='Section'),
        ),
        migrations.AlterField(
            model_name='tpmactivity',
            name='tpm_visit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tpm_activities', to='tpm.TPMVisit', verbose_name='Visit'),
        ),
        migrations.AlterField(
            model_name='tpmvisit',
            name='approval_comment',
            field=models.TextField(blank=True, verbose_name='Approval Comments'),
        ),
        migrations.AlterField(
            model_name='tpmvisit',
            name='reject_comment',
            field=models.TextField(blank=True, verbose_name='Request For More Information'),
        ),
        migrations.AlterField(
            model_name='tpmvisit',
            name='status',
            field=django_fsm.FSMField(choices=[('draft', 'Draft'), ('assigned', 'Assigned'), ('cancelled', 'Cancelled'), ('tpm_accepted', 'TPM Accepted'), ('tpm_rejected', 'TPM Rejected'), ('tpm_reported', 'TPM Reported'), ('tpm_report_rejected', 'Sent Back to TPM'), ('unicef_approved', 'UNICEF Approved')], default='draft', max_length=20, protected=True, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='tpmvisitreportrejectcomment',
            name='reject_reason',
            field=models.TextField(verbose_name='Reason of Rejection'),
        ),
        migrations.AlterField(
            model_name='tpmvisitreportrejectcomment',
            name='rejected_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Rejected At'),
        ),
        migrations.AlterField(
            model_name='tpmvisitreportrejectcomment',
            name='tpm_visit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_reject_comments', to='tpm.TPMVisit', verbose_name='Visit'),
        ),
    ]
