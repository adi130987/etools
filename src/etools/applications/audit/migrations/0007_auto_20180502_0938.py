# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-02 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0006_delete_auditpermission'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='detailedfindinginfo',
            options={'ordering': ('id',), 'verbose_name': 'Detailed Finding Info',
                     'verbose_name_plural': 'Detailed Findings Info'},
        ),
        migrations.AlterModelOptions(
            name='engagementactionpoint',
            options={'ordering': ('id',), 'verbose_name': 'Engagement Action Point',
                     'verbose_name_plural': 'Engagement Action Points'},
        ),
        migrations.AlterModelOptions(
            name='finding',
            options={'ordering': ('id',), 'verbose_name': 'Finding', 'verbose_name_plural': 'Findings'},
        ),
        migrations.AlterModelOptions(
            name='risk',
            options={'ordering': ('id',)},
        ),
        migrations.AlterModelOptions(
            name='riskblueprint',
            options={'ordering': ('order',), 'verbose_name_plural': 'Risk Blueprints'},
        ),
        migrations.AlterModelOptions(
            name='riskcategory',
            options={'ordering': ('order',), 'verbose_name_plural': 'Risk Categories'},
        ),
        migrations.AlterModelOptions(
            name='specialauditrecommendation',
            options={'ordering': ('id',), 'verbose_name': 'Special Audit Recommendation',
                     'verbose_name_plural': 'Special Audit Recommendations'},
        ),
        migrations.AlterModelOptions(
            name='specificprocedure',
            options={'ordering': ('id',), 'verbose_name': 'Specific Procedure',
                     'verbose_name_plural': 'Specific Procedures'},
        ),
    ]
