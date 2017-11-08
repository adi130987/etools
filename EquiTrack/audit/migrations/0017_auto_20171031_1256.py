# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-10-31 12:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def migrate_numbers(apps, schema_editor):
    Engagement = apps.get_model('audit', 'Engagement')
    PurchaseOrder = apps.get_model('audit', 'PurchaseOrder')
    PurchaseOrderItem = apps.get_model('audit', 'PurchaseOrderItem')

    numbers = {}
    for po in PurchaseOrder.objects.all():
        if po.item_number:
            numbers[po.id] = PurchaseOrderItem.objects.create(purchase_order=po, number=po.item_number)

    for engagement in Engagement.objects.select_related('agreement'):
        po = engagement.agreement
        po_item = numbers.get(po.id, None)

        if po_item:
            engagement.po_item = po_item
            engagement.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0016_auto_20171025_0842'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseOrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='PO Item Number')),
            ],
        ),
        migrations.AddField(
            model_name='purchaseorderitem',
            name='purchase_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='audit.PurchaseOrder'),
        ),
        migrations.AlterUniqueTogether(
            name='purchaseorderitem',
            unique_together=set([('purchase_order', 'number')]),
        ),
        migrations.AddField(
            model_name='engagement',
            name='po_item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='audit.PurchaseOrderItem', verbose_name='PO Item Number'),
        ),
        migrations.RunPython(
            migrate_numbers,
            do_nothing,
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='item_number',
        ),
    ]
