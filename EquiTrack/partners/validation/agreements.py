from __future__ import unicode_literals

import logging
from datetime import date

from EquiTrack.validation_mixins import TransitionError, CompleteValidation, check_rigid_fields, StateValidError, \
    check_required_fields, BasicValidationError
from partners.permissions import AgreementPermissions


def agreement_transition_to_signed_valid(agreement):
    today = date.today()
    if agreement.agreement_type == agreement.PCA and \
            agreement.__class__.objects.filter(partner=agreement.partner,
                                               status=agreement.SIGNED,
                                               agreement_type=agreement.PCA,
                                               country_programme=agreement.country_programme).count():

        raise TransitionError(['agreement_transition_to_active_invalid_PCA'])

    if not agreement.start or agreement.start >= today:
        raise TransitionError(['Agreement cannot transition to signed until start date greater or equal to today'])
    if not agreement.end or agreement.end < today:
        raise TransitionError(['Agreement cannot transition to signed end date has passed'])

    return True


def agreement_transition_to_ended_valid(agreement):
    today = date.today()
    logging.debug('I GOT CALLED to ended')
    if agreement.status == agreement.SIGNED and agreement.end and agreement.end < today:
        return True
    raise TransitionError(['agreement_transition_to_ended_invalid'])


def agreements_illegal_transition(agreement):
    return False


def agreements_illegal_transition_permissions(agreement, user):
    logging.debug(agreement.old_instance)
    logging.debug(user)
    # The type of validation that can be done on the user:
    # if user.first_name != 'Rob':
    #     raise TransitionError(['user is not Rob'])
    return True


def amendments_valid(agreement):
    today = date.today()
    for a in agreement.amendments.all():
        if not getattr(a, a.signed_amendment, 'name'):
            return False
        if not a.signed_date or a.signed_date > today:
            return False
    return True


def start_end_dates_valid(agreement):
    if agreement.start and agreement.end and agreement.start > agreement.end:
        return False
    return True


def signed_by_everyone_valid(agreement):
    if not agreement.signed_by_partner_date and agreement.signed_by_unicef_date:
        return False
    return True


def signatures_valid(agreement):
    today = date.today()
    if (agreement.signed_by_unicef_date and not agreement.signed_by) or \
            (agreement.signed_by_partner_date and not agreement.partner_manager) or \
            (agreement.signed_by_partner_date and agreement.signed_by_partner_date > today) or \
            (agreement.signed_by_unicef_date and agreement.signed_by_unicef_date > today):
        return False
    return True


def partner_type_valid_cso(agreement):
    if agreement.agreement_type in ["PCA", "SSFA"] and agreement.partner \
            and not agreement.partner.partner_type == "Civil Society Organization":
        return False
    return True


def ssfa_static(agreement):
    if agreement.agreement_type == agreement.SSFA:
        if agreement.interventions.all().count():
            # there should be only one.. there is a different validation that ensures this
            intervention = agreement.interventions.all().first()
            if intervention.start != agreement.start or intervention.end != agreement.end:
                raise BasicValidationError(_("Start and end dates don't match the Document's start and end"))
    return True



class AgreementValid(CompleteValidation):

    VALIDATION_CLASS = 'partners.Agreement'

    # validations that will be checked on every object... these functions only take the new instance
    BASIC_VALIDATIONS = [
        start_end_dates_valid,
        signatures_valid,
        partner_type_valid_cso,
        amendments_valid,
        ssfa_static
    ]

    VALID_ERRORS = {
        'start_end_dates_valid': 'Agreement start date needs to be earlier than end date',
        'signatures_valid': 'Agreement needs to be signed by UNICEF and Partner, none of the dates can be in'
                            ' the future; if dates are set, signatories are required',
        'generic_transition_fail': 'GENERIC TRANSITION FAIL',
        'suspended_invalid': 'Cant suspend an agreement that was supposed to be ended',
        'agreement_transition_to_active_invalid': "You can't transition to active without having the proper signatures",
        'agreement_transition_to_active_invalid_PCA': "You cannot have more than 1 PCA active per Partner within 1 CP",
        'partner_type_valid_cso': 'Partner type must be CSO for PCA or SSFA agreement types.',
        'end_date_country_programme_valid': 'PCA cannot end after current Country Programme.',
        'amendments_valid': {'signed_amendment': ['Please check that the Document is attached and'
                                                  ' signatures are not in the future']},
    }

    PERMISSIONS_CLASS = AgreementPermissions

    def check_required_fields(self, intervention):
        required_fields = [f for f in self.permissions['required'] if self.permissions['required'][f] is True]
        required_valid, field = check_required_fields(intervention, required_fields)
        if not required_valid:
            raise StateValidError(['Required fields not completed in {}: {}'.format(intervention.status, field)])

    def check_rigid_fields(self, intervention, related=False):
        # this can be set if running in a task and old_instance is not set
        if self.disable_rigid_check:
            return
        rigid_fields = [f for f in self.permissions['edit'] if self.permissions['edit'][f] is False]
        rigid_valid, field = check_rigid_fields(intervention, rigid_fields, related=related)
        if not rigid_valid:
            raise StateValidError(['Cannot change fields while in {}: {}'.format(intervention.status, field)])

    def state_signed_valid(self, agreement, user=None):
        self.check_required_fields(agreement)
        self.check_rigid_fields(agreement, related=True)
        return True

    def state_ended_valid(self, agreement, user=None):
        today = date.today()
        if not today > agreement.end:
            raise StateValidError([_('Today is not after the end date')])
        return True
