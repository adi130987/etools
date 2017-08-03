# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-07-12 18:58
from __future__ import unicode_literals

from django.db import migrations


def email_templates(apps, schema_editor):
    EmailTemplate = apps.get_model('post_office', 'EmailTemplate')

    template, created = EmailTemplate.objects.update_or_create(
        name='partners/partnership/signed/frs',
        defaults={
            'description': 'Partnership signed with future start date that has no Fund Reservations',
            'subject': 'eTools Intervention {{ number }} does not have any FRs',
            'content': """
            Dear Colleague,

            Please note that the Partnership ref. {{ number }} with {{ partner }} is signed, the start date for the PD/SSFA is {{ start_date }} and there is no FR associated with this partnership in eTools.
            Please log into eTools and add the FR number to the record, so that the programme document/SSFA status can change to active.

            {{ url }}.

            Please note that this is an automated message and any response to this email cannot be replied to.
            """
        }
    )

    template, created = EmailTemplate.objects.update_or_create(
        name='partners/partnership/ended/frs/outstanding',
        defaults={
            'description': 'PD Status “ended” And FR Amount does not equal the Actual Amount.',
            'subject': 'eTools Partnership {{ number }} Fund Reservations',
            'content': """
            Dear Colleague,

            Please note that the Partnership ref. {{ number }} with {{ partner }} has ended but the disbursement amount is less than the FR amount.
            Please follow-up with the IP or adjust your FR.

            {{ url }}.

            Please note that this is an automated message and any response to this email cannot be replied to.
            """,
        }
    )

    template, created = EmailTemplate.objects.update_or_create(
        name='partners/partnership/ending',
        defaults={
            'description': 'PD Ending in 30 or 15 days.',
            'subject': 'eTools Partnership {{ number }} is ending in {{ days }} days',
            'content': """
            Dear Colleague,

            Please note that the Partnership ref {{ number }} with {{ partner }} will end in {{ days }} days.
            Please follow-up with the Implementing Partner on status of implementation, which may require an amendment.

            {{ url }}.

            Please note that this is an automated message and any response to this email cannot be replied to.
            """
        }
    )


def delete_email_templates(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_auto_20170125_0037'),
    ]

    operations = [
        migrations.RunPython(email_templates, reverse_code=delete_email_templates)
    ]
