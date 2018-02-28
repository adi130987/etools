from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import json

from EquiTrack.factories import PartnerFactory
from EquiTrack.tests.cases import EToolsTenantTestCase
from partners.models import PartnerOrganization
from users.models import Country
from vision.adapters import partner as adapter


class TestPartnerSynchronizer(EToolsTenantTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.first()

    def setUp(self):
        self.data = {
            "PARTNER_TYPE_DESC": "UN AGENCY",
            "VENDOR_NAME": "ACME Inc.",
            "VENDOR_CODE": "ACM",
            "COUNTRY": "USD",
            "TOTAL_CASH_TRANSFERRED_CP": "150.00",
            "TOTAL_CASH_TRANSFERRED_CY": "100.00",
            "NET_CASH_TRANSFERRED_CY": "90.00",
            "REPORTED_CY": "80.00",
            "TOTAL_CASH_TRANSFERRED_YTD": "70.00",
        }
        self.records = {"ROWSET": {"ROW": [self.data]}}
        self.adapter = adapter.PartnerSynchronizer(self.country)

    def test_convert_records(self):
        self.assertEqual(
            self.adapter._convert_records(json.dumps(self.records)),
            [self.data]
        )

    def test_filter_records(self):
        """Ensure records maintained"""
        response = self.adapter._filter_records([self.data])
        self.assertEqual(response, [self.data])

    def test_filter_records_no_vendor_name(self):
        """If missing vendor name ignore record"""
        self.data["VENDOR_NAME"] = ""
        response = self.adapter._filter_records([self.data])
        self.assertEqual(response, [])

    def test_get_json(self):
        response = self.adapter._get_json(self.data)
        self.assertEqual(response, self.data)

    def test_get_json_no_data(self):
        response = self.adapter._get_json(adapter.VISION_NO_DATA_MESSAGE)
        self.assertEqual(response, [])

    def test_save_records_no_type(self):
        """Check that partner organization record is created,
        no type mapping
        """
        self.data["PARTNER_TYPE_DESC"] = "Supplier"
        self.data["VENDOR_CODE"] = "123"
        partner_qs = PartnerOrganization.objects.filter(
            vendor_number=self.data["VENDOR_CODE"]
        )
        self.assertFalse(partner_qs.exists())
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 0)
        self.assertTrue(partner_qs.exists())
        partner = partner_qs.first()
        self.assertEqual(partner.name, "")

    def test_save_records(self):
        """Check that partner organization record is created,
        type mapping matches
        """
        self.data["VENDOR_CODE"] = "124"
        partner_qs = PartnerOrganization.objects.filter(
            vendor_number=self.data["VENDOR_CODE"]
        )
        self.assertFalse(partner_qs.exists())
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 1)
        self.assertTrue(partner_qs.exists())
        partner = partner_qs.first()
        self.assertEqual(partner.name, self.data["VENDOR_NAME"])

    def test_save_records_update_name(self):
        """Check that partner organization record is updated,
        name changed
        """
        partner = PartnerFactory(
            name="New",
            vendor_number=self.data["VENDOR_CODE"]
        )
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 1)
        partner_updated = PartnerOrganization.objects.get(pk=partner.pk)
        self.assertEqual(partner_updated.name, self.data["VENDOR_NAME"])

    def test_save_records_update_partner_type(self):
        """Check that partner organization record is updated,
        partner type changed
        """
        partner = PartnerFactory(
            name=self.data["VENDOR_NAME"],
            vendor_number=self.data["VENDOR_CODE"],
            country=self.data["COUNTRY"],
            partner_type="Government",
        )
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 1)
        partner_updated = PartnerOrganization.objects.get(pk=partner.pk)
        self.assertEqual(partner_updated.partner_type, "UN Agency")

    def test_save_records_update_deleted_flag(self):
        """Check that partner organization record is updated,
        deleted_flag changed
        """
        self.data["MARKED_FOR_DELETION"] = True
        partner = PartnerFactory(
            name=self.data["VENDOR_NAME"],
            vendor_number=self.data["VENDOR_CODE"],
            deleted_flag=False
        )
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 1)
        partner_updated = PartnerOrganization.objects.get(pk=partner.pk)
        self.assertTrue(partner_updated.deleted_flag)

    def test_save_records_update_blocked(self):
        """Check that partner organization record is updated,
        blocked changed
        """
        self.data["POSTING_BLOCK"] = True
        partner = PartnerFactory(
            name=self.data["VENDOR_NAME"],
            vendor_number=self.data["VENDOR_CODE"],
            country=self.data["COUNTRY"],
            blocked=False
        )
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 1)
        partner_updated = PartnerOrganization.objects.get(pk=partner.pk)
        self.assertTrue(partner_updated.blocked)

    def test_save_records_update_date(self):
        """Check that partner organization record is updated,
        last assessment date changed
        """
        self.data["DATE_OF_ASSESSMENT"] = "4-Apr-17"
        partner = PartnerFactory(
            name=self.data["VENDOR_NAME"],
            vendor_number=self.data["VENDOR_CODE"],
            country=self.data["COUNTRY"],
            last_assessment_date=datetime.date(2017, 4, 5),
        )
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 1)
        partner_updated = PartnerOrganization.objects.get(pk=partner.pk)
        self.assertEqual(
            partner_updated.last_assessment_date,
            datetime.date(2017, 4, 4)
        )

    def test_save_records_update(self):
        """Check that partner organization record is NOT updated,
        if no change
        """
        PartnerFactory(
            name=self.data["VENDOR_NAME"],
            vendor_number=self.data["VENDOR_CODE"],
            country=self.data["COUNTRY"],
            partner_type="UN Agency",
            total_ct_cp=self.data["TOTAL_CASH_TRANSFERRED_CP"],
            total_ct_cy=self.data["TOTAL_CASH_TRANSFERRED_CY"],
        )
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 1)
