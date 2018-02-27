# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-01-20 07:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0027_remove_audit_percent_of_audited_expenditure'),
    ]

    operations = [
        migrations.RenameField(
            model_name='engagementactionpoint',
            old_name='description',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='engagementactionpoint',
            old_name='comments',
            new_name='description',
        ),
        migrations.AlterField(
            model_name='engagementactionpoint',
            name='category',
            field=models.CharField(choices=[('Invoice and receive reimbursement of ineligible expenditure', 'Invoice and receive reimbursement of ineligible expenditure'), ('Change cash transfer modality (DCT, reimbursement or direct payment)', 'Change cash transfer modality (DCT, reimbursement or direct payment)'), ('IP to incur and report on additional expenditure', 'IP to incur and report on additional expenditure'), ('Review and amend ICE or budget', 'Review and amend ICE or budget'), ('IP to correct FACE form or Statement of Expenditure', 'IP to correct FACE form or Statement of Expenditure'), ('Schedule a programmatic visit', 'Schedule a programmatic visit'), ('Schedule a follow-up spot check', 'Schedule a follow-up spot check'), ('Schedule an audit', 'Schedule an audit'), ('Block future cash transfers', 'Block future cash transfers'), ('Block or mark vendor for deletion', 'Block or mark vendor for deletion'), ('Escalate to Chief of Operations, Dep Rep, or Rep', 'Escalate to Chief of Operations, Dep Rep, or Rep'), ('Escalate to Investigation', 'Escalate to Investigation'), ('Capacity building / Discussion with partner', 'Capacity building / Discussion with partner'), ('Change IP risk rating', 'Change IP risk rating'), ('Other', 'Other')], max_length=100, verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='engagementactionpoint',
            name='description',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='engagementactionpoint',
            name='action_taken',
            field=models.TextField(blank=True, verbose_name='Action Taken'),
        ),
        migrations.AddField(
            model_name='engagementactionpoint',
            name='status',
            field=models.CharField(choices=[('open', 'Open'), ('closed', 'Closed')], default='open', max_length=10, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='engagementactionpoint',
            name='high_priority',
            field=models.BooleanField(default=False, verbose_name='High Priority'),
        ),
    ]