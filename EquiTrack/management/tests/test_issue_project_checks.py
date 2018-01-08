from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import override_settings

from EquiTrack.factories import (
    AgreementFactory,
    CountryProgrammeFactory,
    InterventionFactory,
    ResultFactory,
    UserFactory,
)
from EquiTrack.tests.mixins import FastTenantTestCase
from management.models import FlaggedIssue
from management.issues import checks
from partners.models import Agreement, Intervention, InterventionResultLink


class TestActivePCANoSignedDocCheck(FastTenantTestCase):
    def setUp(self):
        super(TestActivePCANoSignedDocCheck, self).setUp()
        UserFactory(username="etools_task_admin")

    @override_settings(ISSUE_CHECKS=['management.issues.project_checks.ActivePCANoSignedDocCheck'])
    def test_issue_found(self):
        """Check that if no attached agreement, then an issue is raised"""
        qs_issue = FlaggedIssue.objects.filter(
            issue_id="active_pca_no_signed_doc"
        )
        agreement = AgreementFactory(attached_agreement=None)
        self.assertFalse(agreement.attached_agreement)
        self.assertEqual(agreement.agreement_type, Agreement.PCA)

        self.assertFalse(qs_issue.exists())
        checks.bootstrap_checks(default_is_active=True)
        checks.run_all_checks()
        self.assertTrue(qs_issue.exists())
        issue = qs_issue.first()
        self.assertIn("does not have a signed PCA attached", issue.message)

    def test_no_issue(self):
        """Check that is attached agreement, then no issue"""
        qs_issue = FlaggedIssue.objects.filter(
            issue_id="active_pca_no_signed_doc"
        )
        agreement = AgreementFactory()
        self.assertTrue(agreement.attached_agreement)
        self.assertEqual(agreement.agreement_type, Agreement.PCA)

        self.assertFalse(qs_issue.exists())
        checks.bootstrap_checks(default_is_active=True)
        checks.run_all_checks()
        self.assertFalse(qs_issue.exists())


class TestPdOutputsWrongCheck(FastTenantTestCase):
    def setUp(self):
        super(TestPdOutputsWrongCheck, self).setUp()
        UserFactory(username="etools_task_admin")

    @override_settings(ISSUE_CHECKS=['management.issues.project_checks.PdOutputsWrongCheck'])
    def test_issue_found(self):
        """Check that is country programme for intervention does not
        match result country programme then issue is created"""
        qs_issue = FlaggedIssue.objects.filter(
            issue_id="pd_outputs_wrong"
        )
        start_date = datetime.date(2001, 1, 1)
        end_date = datetime.date(2001, 12, 31)
        country = CountryProgrammeFactory(
            from_date=start_date,
            to_date=end_date,
        )
        intervention = InterventionFactory(
            country_programme=country,
            start=start_date,
        )
        result = ResultFactory(country_programme=CountryProgrammeFactory())
        InterventionResultLink.objects.create(
            intervention=intervention,
            cp_output=result,
        )
        self.assertNotEqual(
            intervention.country_programme,
            result.country_programme
        )

        self.assertFalse(qs_issue.exists())
        checks.bootstrap_checks(default_is_active=True)
        checks.run_all_checks()
        self.assertTrue(qs_issue.exists())
        issue = qs_issue.first()
        self.assertIn("has wrongly mapped outputs", issue.message)

    @override_settings(ISSUE_CHECKS=['management.issues.project_checks.PdOutputsWrongCheck'])
    def test_no_interventions(self):
        """If intervention does not fit in with Country Programmes
        then no issues raised
        """
        qs_issue = FlaggedIssue.objects.filter(
            issue_id="pd_outputs_wrong"
        )
        start_date = datetime.date(2001, 1, 1)
        end_date = datetime.date(2001, 12, 31)
        country = CountryProgrammeFactory(
            from_date=start_date,
            to_date=end_date,
        )
        intervention = InterventionFactory(
            country_programme=country,
            start=start_date - datetime.timedelta(days=1),
        )
        result = ResultFactory(country_programme=CountryProgrammeFactory())
        InterventionResultLink.objects.create(
            intervention=intervention,
            cp_output=result,
        )
        self.assertNotEqual(
            intervention.country_programme,
            result.country_programme
        )

        self.assertFalse(qs_issue.exists())
        checks.bootstrap_checks(default_is_active=True)
        checks.run_all_checks()
        self.assertFalse(qs_issue.exists())

    @override_settings(ISSUE_CHECKS=['management.issues.project_checks.PdOutputsWrongCheck'])
    def test_no_country_programme(self):
        """Check that if intervention has no country programme
        the intervention is ignored during the check
        """
        qs_issue = FlaggedIssue.objects.filter(
            issue_id="pd_outputs_wrong"
        )
        intervention = InterventionFactory()
        result = ResultFactory(country_programme=CountryProgrammeFactory())
        InterventionResultLink.objects.create(
            intervention=intervention,
            cp_output=result,
        )
        self.assertIsNone(intervention.country_programme)
        self.assertNotEqual(
            intervention.country_programme,
            result.country_programme
        )

        self.assertFalse(qs_issue.exists())
        checks.bootstrap_checks(default_is_active=True)
        checks.run_all_checks()
        self.assertFalse(qs_issue.exists())

    @override_settings(ISSUE_CHECKS=['management.issues.project_checks.PdOutputsWrongCheck'])
    def test_no_issue(self):
        """Check that valida interventions results in no issue"""
        qs_issue = FlaggedIssue.objects.filter(
            issue_id="pd_outputs_wrong"
        )
        start_date = datetime.date(2001, 1, 1)
        end_date = datetime.date(2001, 12, 31)
        country = CountryProgrammeFactory(
            from_date=start_date,
            to_date=end_date,
        )
        intervention = InterventionFactory(
            country_programme=country,
            start=start_date,
        )
        result = ResultFactory(country_programme=country)
        InterventionResultLink.objects.create(
            intervention=intervention,
            cp_output=result,
        )
        self.assertEqual(
            intervention.country_programme,
            result.country_programme
        )

        self.assertFalse(qs_issue.exists())
        checks.bootstrap_checks(default_is_active=True)
        checks.run_all_checks()
        self.assertFalse(qs_issue.exists())


class TestInterventionsAssociatedSSFACheck(FastTenantTestCase):
    def setUp(self):
        super(TestInterventionsAssociatedSSFACheck, self).setUp()
        self.qs_issue = FlaggedIssue.objects.filter(
            issue_id="interventions_associated_ssfa"
        )

    @override_settings(ISSUE_CHECKS=['management.issues.project_checks.InterventionsAssociatedSSFACheck'])
    def test_document_type_pd(self):
        """Check that if agreement type SSFA but document type PD
        then issue is raised
        """
        agreement = AgreementFactory(agreement_type=Agreement.SSFA)
        InterventionFactory(
            agreement=agreement,
            document_type=Intervention.PD,
        )
        self.assertFalse(self.qs_issue.exists())
        checks.bootstrap_checks(default_is_active=True)
        checks.run_all_checks()
        self.assertTrue(self.qs_issue.exists())
        issue = self.qs_issue.first()
        self.assertIn("type {}".format(Intervention.PD), issue.message)

    @override_settings(ISSUE_CHECKS=['management.issues.project_checks.InterventionsAssociatedSSFACheck'])
    def test_document_type_ssfa(self):
        """Check that if agreement type PCA but document type SSFA
        then issue is raised
        """
        agreement = AgreementFactory(agreement_type=Agreement.PCA)
        InterventionFactory(
            agreement=agreement,
            document_type=Intervention.SSFA,
        )
        self.assertFalse(self.qs_issue.exists())
        checks.bootstrap_checks(default_is_active=True)
        checks.run_all_checks()
        self.assertTrue(self.qs_issue.exists())
        issue = self.qs_issue.first()
        self.assertIn("type {}".format(Intervention.SSFA), issue.message)

    @override_settings(ISSUE_CHECKS=['management.issues.project_checks.InterventionsAssociatedSSFACheck'])
    def test_no_issue_pd(self):
        """Check that if agreement type SSFA and document type PD
        then issue is NOT raised
        """
        agreement = AgreementFactory(agreement_type=Agreement.SSFA)
        InterventionFactory(
            agreement=agreement,
            document_type=Intervention.SSFA,
        )
        self.assertFalse(self.qs_issue.exists())
        checks.bootstrap_checks(default_is_active=True)
        checks.run_all_checks()
        self.assertFalse(self.qs_issue.exists())

    @override_settings(ISSUE_CHECKS=['management.issues.project_checks.InterventionsAssociatedSSFACheck'])
    def test_no_issue_ssfa(self):
        """Check that if agreement type PCA and document type SSFA
        then issue is NOT raised
        """
        agreement = AgreementFactory(agreement_type=Agreement.PCA)
        InterventionFactory(
            agreement=agreement,
            document_type=Intervention.PD,
        )
        self.assertFalse(self.qs_issue.exists())
        checks.bootstrap_checks(default_is_active=True)
        checks.run_all_checks()
        self.assertFalse(self.qs_issue.exists())
