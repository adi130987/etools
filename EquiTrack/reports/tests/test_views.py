import datetime

from unittest import TestCase

from django.core.urlresolvers import reverse
from rest_framework import status
from tablib.core import Dataset

from reports.models import ResultType, CountryProgramme
from EquiTrack.factories import (
    AppliedIndicatorFactory,
    IndicatorBlueprintFactory,
    InterventionResultLinkFactory,
    LowerResultFactory,
    UserFactory,
    ResultFactory,
    SectionFactory,
    LocationFactory,
    CountryProgrammeFactory,
)
from EquiTrack.tests.mixins import APITenantTestCase, URLAssertionMixin


class TestReportViews(APITenantTestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.unicef_staff = UserFactory(is_staff=True)
        self.result_type = ResultType.objects.get(name=ResultType.OUTPUT)

        today = datetime.date.today()
        self.country_programme = CountryProgrammeFactory(
            wbs='0000/A0/01',
            from_date=datetime.date(today.year - 1, 1, 1),
            to_date=datetime.date(today.year + 1, 1, 1))

        self.result1 = ResultFactory(
            result_type=self.result_type,
            country_programme=self.country_programme,
        )

        self.result2 = ResultFactory(
            result_type=self.result_type,
            country_programme=self.country_programme
        )

        # Additional data to use in tests
        self.location1 = LocationFactory()
        self.location3 = LocationFactory()
        self.section1 = SectionFactory()
        self.section3 = SectionFactory()

    def test_api_resulttypes_list(self):
        response = self.forced_auth_req('get', '/api/reports/result-types/', user=self.unicef_staff)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_sectors_list(self):
        response = self.forced_auth_req('get', '/api/reports/sectors/', user=self.unicef_staff)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_indicators_list(self):
        response = self.forced_auth_req('get', '/api/reports/indicators/', user=self.unicef_staff)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_results_list(self):
        response = self.forced_auth_req('get', '/api/reports/results/', user=self.unicef_staff)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(int(response.data[0]["id"]), self.result1.id)

    def test_api_results_patch(self):
        url = '/api/reports/results/{}/'.format(self.result1.id)
        data = {"name": "patched name"}
        response = self.forced_auth_req('patch', url, user=self.unicef_staff, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "patched name")

    def test_api_units_list(self):
        response = self.forced_auth_req('get', '/api/reports/units/', user=self.unicef_staff)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_apiv2_results_list(self):
        response = self.forced_auth_req(
            'get',
            reverse('report-result-list'),
            user=self.unicef_staff
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(int(response.data[0]["id"]), self.result1.id)

    def test_apiv2_results_list_minimal(self):
        params = {"verbosity": "minimal"}
        response = self.forced_auth_req(
            'get',
            reverse('report-result-list'),
            user=self.unicef_staff,
            data=params,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0].keys(), ["id", "name"])

    def test_apiv2_results_retrieve(self):
        response = self.forced_auth_req(
            'get',
            reverse('report-result-detail', args=[self.result1.id]),
            user=self.unicef_staff
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(int(response.data["id"]), self.result1.id)

    def test_apiv2_results_list_current_cp(self):
        response = self.forced_auth_req(
            'get',
            reverse('report-result-list'),
            user=self.unicef_staff
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(int(response.data[0]["country_programme"]), CountryProgramme.objects.all_active.first().id)

    def test_apiv2_results_list_filter_year(self):
        param = {
            "year": datetime.date.today().year,
        }
        response = self.forced_auth_req(
            'get',
            reverse('report-result-list'),
            user=self.unicef_staff,
            data=param,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_apiv2_results_list_filter_cp(self):
        param = {
            "country_programme": self.result1.country_programme.id,
        }
        response = self.forced_auth_req(
            'get',
            reverse('report-result-list'),
            user=self.unicef_staff,
            data=param,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(int(response.data[0]["id"]), self.result1.id)

    def test_apiv2_results_list_filter_result_type(self):
        param = {
            "result_type": self.result_type.name,
        }
        response = self.forced_auth_req(
            'get',
            reverse('report-result-list'),
            user=self.unicef_staff,
            data=param,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(int(response.data[0]["id"]), self.result1.id)

    def test_apiv2_results_list_filter_values(self):
        param = {
            "values": '{},{}'.format(self.result1.id, self.result2.id)
        }
        response = self.forced_auth_req(
            'get',
            reverse('report-result-list'),
            user=self.unicef_staff,
            data=param,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_apiv2_results_list_filter_values_bad(self):
        param = {
            "values": '{},{}'.format('23fg', 'aasd67')
        }
        response = self.forced_auth_req(
            'get',
            reverse('report-result-list'),
            user=self.unicef_staff,
            data=param,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['ID values must be integers'])

    def test_apiv2_results_list_filter_combined(self):
        param = {
            "result_type": self.result_type.name,
            "year": datetime.date.today().year,
        }
        response = self.forced_auth_req(
            'get',
            reverse('report-result-list'),
            user=self.unicef_staff,
            data=param,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.result1.id, [int(i["id"]) for i in response.data])


class UrlsTestCase(URLAssertionMixin, TestCase):
    '''Simple test case to verify URL reversal'''
    def test_urls(self):
        '''Verify URL pattern names generate the URLs we expect them to.'''
        names_and_paths = (
            ('applied-indicator', 'applied-indicators/', {}),
            ('lower-results', 'lower_results/', {}),
        )
        self.assertReversal(names_and_paths, '', '/api/v2/reports/')


class TestLowerResultExportList(APITenantTestCase):
    def setUp(self):
        super(TestLowerResultExportList, self).setUp()
        self.unicef_staff = UserFactory(is_staff=True)
        self.result_link = InterventionResultLinkFactory()
        self.lower_result = LowerResultFactory(
            result_link=self.result_link
        )

    def test_invalid_format_export_api(self):
        response = self.forced_auth_req(
            'get',
            reverse('lower-results'),
            user=self.unicef_staff,
            data={"format": "unknown"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_csv_export_api(self):
        response = self.forced_auth_req(
            'get',
            reverse('lower-results'),
            user=self.unicef_staff,
            data={"format": "csv"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dataset = Dataset().load(response.content, 'csv')
        self.assertEqual(dataset.height, 1)
        self.assertEqual(len(dataset._get_headers()), 6)
        self.assertEqual(len(dataset[0]), 6)

    def test_csv_flat_export_api(self):
        response = self.forced_auth_req(
            'get',
            reverse('lower-results'),
            user=self.unicef_staff,
            data={"format": "csv_flat"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dataset = Dataset().load(response.content, 'csv')
        self.assertEqual(dataset.height, 1)
        self.assertEqual(len(dataset._get_headers()), 6)
        self.assertEqual(len(dataset[0]), 6)


class TestAppliedIndicatorExportList(APITenantTestCase):
    def setUp(self):
        super(TestAppliedIndicatorExportList, self).setUp()
        self.unicef_staff = UserFactory(is_staff=True)
        self.result_link = InterventionResultLinkFactory()
        self.lower_result = LowerResultFactory(
            result_link=self.result_link
        )
        self.indicator = IndicatorBlueprintFactory()
        self.applied = AppliedIndicatorFactory(
            indicator=self.indicator,
            lower_result=self.lower_result
        )

    def test_invalid_format_export_api(self):
        response = self.forced_auth_req(
            'get',
            reverse('applied-indicator'),
            user=self.unicef_staff,
            data={"format": "unknown"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_csv_export_api(self):
        response = self.forced_auth_req(
            'get',
            reverse('applied-indicator'),
            user=self.unicef_staff,
            data={"format": "csv"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dataset = Dataset().load(response.content, 'csv')
        self.assertEqual(dataset.height, 1)
        self.assertEqual(len(dataset._get_headers()), 17)
        self.assertEqual(len(dataset[0]), 17)

    def test_csv_flat_export_api(self):
        response = self.forced_auth_req(
            'get',
            reverse('applied-indicator'),
            user=self.unicef_staff,
            data={"format": "csv_flat"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dataset = Dataset().load(response.content, 'csv')
        self.assertEqual(dataset.height, 1)
        self.assertEqual(len(dataset._get_headers()), 17)
        self.assertEqual(len(dataset[0]), 17)
