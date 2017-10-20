# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-10-20 09:58
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import partners.models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0053_auto_20171011_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agreement',
            name='agreement_type',
            field=models.CharField(choices=[('PCA', 'Programme Cooperation Agreement'), ('SSFA', 'Small Scale Funding Agreement'), ('MOU', 'Memorandum of Understanding')], max_length=10, verbose_name='Agreement Type'),
        ),
        migrations.AlterField(
            model_name='agreement',
            name='attached_agreement',
            field=models.FileField(blank=True, max_length=1024, upload_to=partners.models.get_agreement_path, verbose_name='Attached Agreement'),
        ),
        migrations.AlterField(
            model_name='agreement',
            name='authorized_officers',
            field=models.ManyToManyField(blank=True, related_name='agreement_authorizations', to='partners.PartnerStaffMember', verbose_name='Partner Authorized Officer'),
        ),
        migrations.AlterField(
            model_name='agreement',
            name='country_programme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agreements', to='reports.CountryProgramme', verbose_name='Country Programme'),
        ),
        migrations.AlterField(
            model_name='agreement',
            name='end',
            field=models.DateField(blank=True, null=True, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='agreement',
            name='signed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agreements_signed+', to=settings.AUTH_USER_MODEL, verbose_name='Signed By UNICEF'),
        ),
        migrations.AlterField(
            model_name='agreement',
            name='signed_by_partner_date',
            field=models.DateField(blank=True, null=True, verbose_name='Signed By Partner Date'),
        ),
        migrations.AlterField(
            model_name='agreement',
            name='signed_by_unicef_date',
            field=models.DateField(blank=True, null=True, verbose_name='Signed By UNICEF Date'),
        ),
        migrations.AlterField(
            model_name='agreement',
            name='start',
            field=models.DateField(blank=True, null=True, verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='agreement',
            name='status',
            field=django_fsm.FSMField(blank=True, choices=[('draft', 'Draft'), ('signed', 'Signed'), ('ended', 'Ended'), ('suspended', 'Suspended'), ('terminated', 'Terminated')], default='draft', max_length=32, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='agreementamendment',
            name='agreement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amendments', to='partners.Agreement', verbose_name='Agreement'),
        ),
        migrations.AlterField(
            model_name='agreementamendment',
            name='number',
            field=models.CharField(max_length=5, verbose_name='Number'),
        ),
        migrations.AlterField(
            model_name='agreementamendment',
            name='signed_amendment',
            field=models.FileField(blank=True, max_length=1024, null=True, upload_to=partners.models.get_agreement_amd_file_path, verbose_name='Signed Amendment'),
        ),
        migrations.AlterField(
            model_name='agreementamendment',
            name='signed_date',
            field=models.DateField(blank=True, null=True, verbose_name='Signed Date'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='approving_officer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Approving Officer'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='completed_date',
            field=models.DateField(blank=True, null=True, verbose_name='Completed Date'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='names_of_other_agencies',
            field=models.CharField(blank=True, help_text='List the names of the other agencies they have worked with', max_length=255, null=True, verbose_name='Other Agencies'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessments', to='partners.PartnerOrganization', verbose_name='Partner'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='planned_date',
            field=models.DateField(blank=True, null=True, verbose_name='Planned Date'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='rating',
            field=models.CharField(choices=[('high', 'High'), ('significant', 'Significant'), ('medium', 'Medium'), ('low', 'Low')], default='high', max_length=50, verbose_name='Rating'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='report',
            field=models.FileField(blank=True, max_length=1024, null=True, upload_to=partners.models.get_assesment_path, verbose_name='Report'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='requested_date',
            field=models.DateField(auto_now_add=True, verbose_name='Requested Date'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='requesting_officer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requested_assessments', to=settings.AUTH_USER_MODEL, verbose_name='Requesting Officer'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='type',
            field=models.CharField(choices=[('Micro Assessment', 'Micro Assessment'), ('Simplified Checklist', 'Simplified Checklist'), ('Scheduled Audit report', 'Scheduled Audit report'), ('Special Audit report', 'Special Audit report'), ('Other', 'Other')], max_length=50, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='agreement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interventions', to='partners.Agreement', verbose_name='Agreement'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='contingency_pd',
            field=models.BooleanField(default=False, verbose_name='Contingency PD'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='country_programme',
            field=models.ForeignKey(blank=True, help_text='Which Country Programme does this Intervention belong to?', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='interventions', to='reports.CountryProgramme', verbose_name='Country Programme'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='end',
            field=models.DateField(blank=True, help_text='The date the Intervention will end', null=True, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='metadata',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True, verbose_name='Metadata'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='offices',
            field=models.ManyToManyField(blank=True, related_name='_intervention_offices_+', to='users.Office', verbose_name='UNICEF Office'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='partner_authorized_officer_signatory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='signed_interventions', to='partners.PartnerStaffMember', verbose_name='Signed by Partner'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='partner_focal_points',
            field=models.ManyToManyField(blank=True, related_name='_intervention_partner_focal_points_+', to='partners.PartnerStaffMember', verbose_name='CSO Authorized Officials'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='population_focus',
            field=models.CharField(blank=True, max_length=130, null=True, verbose_name='Population Focus'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='prc_review_document',
            field=models.FileField(blank=True, max_length=1024, null=True, upload_to=partners.models.get_prc_intervention_file_path, verbose_name='Review Document by PRC'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='signed_by_partner_date',
            field=models.DateField(blank=True, null=True, verbose_name='Signed by Partner Date'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='signed_by_unicef_date',
            field=models.DateField(blank=True, null=True, verbose_name='Signed by UNICEF Date'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='signed_pd_document',
            field=models.FileField(blank=True, max_length=1024, null=True, upload_to=partners.models.get_prc_intervention_file_path, verbose_name='Signed PD Document'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='start',
            field=models.DateField(blank=True, help_text='The date the Intervention will start', null=True, verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='status',
            field=django_fsm.FSMField(blank=True, choices=[('draft', 'Draft'), ('signed', 'Signed'), ('active', 'Active'), ('ended', 'Ended'), ('closed', 'Closed'), ('suspended', 'Suspended'), ('terminated', 'Terminated')], default='draft', max_length=32, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='submission_date',
            field=models.DateField(blank=True, help_text='The date the partner submitted complete PD/SSFA documents to Unicef', null=True, verbose_name='Document Submission Date by CSO'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='title',
            field=models.CharField(max_length=256, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='unicef_focal_points',
            field=models.ManyToManyField(blank=True, related_name='_intervention_unicef_focal_points_+', to=settings.AUTH_USER_MODEL, verbose_name='UNICEF Focal Points'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='unicef_signatory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='signed_interventions+', to=settings.AUTH_USER_MODEL, verbose_name='Signed by UNICEF'),
        ),
        migrations.AlterField(
            model_name='interventionamendment',
            name='amendment_number',
            field=models.IntegerField(default=0, verbose_name='Number'),
        ),
        migrations.AlterField(
            model_name='interventionamendment',
            name='intervention',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amendments', to='partners.Intervention', verbose_name='Reference Number'),
        ),
        migrations.AlterField(
            model_name='interventionamendment',
            name='other_description',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='interventionamendment',
            name='signed_amendment',
            field=models.FileField(max_length=1024, upload_to=partners.models.get_intervention_amendment_file_path, verbose_name='Amendment'),
        ),
        migrations.AlterField(
            model_name='interventionamendment',
            name='signed_date',
            field=models.DateField(null=True, verbose_name='Signed Date'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='alternate_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Alternate ID'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='alternate_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Alternate Name'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='blocked',
            field=models.BooleanField(default=False, verbose_name='Blocked'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='city',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='core_values_assessment',
            field=models.FileField(blank=True, help_text='Only required for CSO partners', max_length=1024, null=True, upload_to='partners/core_values/', verbose_name='Core Values Assessment'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='country',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='description',
            field=models.CharField(blank=True, max_length=256, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='email',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Email Address'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='hact_values',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=partners.models.hact_default, null=True, verbose_name='HACT'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Hidden'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='last_assessment_date',
            field=models.DateField(blank=True, null=True, verbose_name='Last Assessment Date'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='partner_type',
            field=models.CharField(choices=[('Bilateral / Multilateral', 'Bilateral / Multilateral'), ('Civil Society Organization', 'Civil Society Organization'), ('Government', 'Government'), ('UN Agency', 'UN Agency')], max_length=50, verbose_name='Partner Type'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='phone_number',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='postal_code',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Postal Code'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='shared_partner',
            field=models.CharField(choices=[('No', 'No'), ('with UNDP', 'with UNDP'), ('with UNFPA', 'with UNFPA'), ('with UNDP & UNFPA', 'with UNDP & UNFPA')], default='No', help_text='Partner shared with UNDP or UNFPA?', max_length=50, verbose_name='Shared Partner (old)'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='short_name',
            field=models.CharField(blank=True, max_length=50, verbose_name='Short Name'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='street_address',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Street Address'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='total_ct_cp',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Total Cash Transferred for Country Programme', max_digits=12, null=True, verbose_name='Total Cash Transferred for Country Programme'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='total_ct_cy',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Total Cash Transferred per Current Year', max_digits=12, null=True, verbose_name='Total Cash Transferred per Current Year'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='type_of_assessment',
            field=models.CharField(max_length=50, null=True, verbose_name='Assessment Type'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='vendor_number',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='Vendor Number'),
        ),
        migrations.AlterField(
            model_name='partnerorganization',
            name='vision_synced',
            field=models.BooleanField(default=False, verbose_name='VISION Synced'),
        ),
        migrations.AlterField(
            model_name='partnerstaffmember',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Active'),
        ),
        migrations.AlterField(
            model_name='partnerstaffmember',
            name='email',
            field=models.CharField(max_length=128, unique=True, verbose_name='Email Address'),
        ),
        migrations.AlterField(
            model_name='partnerstaffmember',
            name='first_name',
            field=models.CharField(max_length=64, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='partnerstaffmember',
            name='last_name',
            field=models.CharField(max_length=64, verbose_name='Last Name'),
        ),
        migrations.AlterField(
            model_name='partnerstaffmember',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_members', to='partners.PartnerOrganization', verbose_name='Partner'),
        ),
        migrations.AlterField(
            model_name='partnerstaffmember',
            name='phone',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='partnerstaffmember',
            name='title',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Title'),
        ),
    ]
