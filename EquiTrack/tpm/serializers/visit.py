import itertools
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from locations.models import Location
from partners.models import InterventionResultLink, Intervention, PartnerOrganization
from partners.serializers.interventions_v2 import InterventionCreateUpdateSerializer, InterventionListSerializer
from reports.models import Result
from tpm.models import TPMVisit, TPMPermission, TPMActivity, TPMVisitReportRejectComment, TPMActivityActionPoint, \
    TPMPartnerStaffMember
from tpm.serializers.attachments import TPMAttachmentsSerializer, TPMReportAttachmentsSerializer, \
    TPMActivityPDSerializer
from utils.permissions.serializers import StatusPermissionsBasedSerializerMixin, \
    StatusPermissionsBasedRootSerializerMixin
from utils.common.serializers.fields import SeparatedReadWriteField
from tpm.serializers.partner import TPMPartnerLightSerializer, TPMPartnerStaffMemberSerializer
from users.serializers import MinimalUserSerializer, OfficeSerializer
from utils.writable_serializers.serializers import WritableNestedSerializerMixin
from users.serializers import SectionSerializer
from locations.serializers import LocationLightSerializer
from reports.serializers.v1 import ResultSerializer


class TPMPermissionsBasedSerializerMixin(StatusPermissionsBasedSerializerMixin):
    class Meta(StatusPermissionsBasedSerializerMixin.Meta):
        permission_class = TPMPermission


class InterventionResultLinkVisitSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="cp_output.name")

    class Meta:
        model = InterventionResultLink
        fields = [
            'id', 'name'
        ]


class PartnerOrganizationLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerOrganization
        fields = [
            'id', 'name'
        ]


class TPMVisitReportRejectCommentSerializer(TPMPermissionsBasedSerializerMixin,
                                            WritableNestedSerializerMixin,
                                            serializers.ModelSerializer):
    class Meta(TPMPermissionsBasedSerializerMixin.Meta, WritableNestedSerializerMixin.Meta):
        model = TPMVisitReportRejectComment
        fields = ['id', 'rejected_at', 'reject_reason', ]


class TPMActivityActionPointSerializer(TPMPermissionsBasedSerializerMixin,
                                       WritableNestedSerializerMixin,
                                       serializers.ModelSerializer):
    author = MinimalUserSerializer(read_only=True)

    person_responsible = SeparatedReadWriteField(
        read_field=MinimalUserSerializer(read_only=True),
        required=True
    )

    is_responsible = serializers.SerializerMethodField()

    def get_is_responsible(self, obj):
        return self.get_user() == obj.person_responsible

    class Meta(TPMPermissionsBasedSerializerMixin.Meta, WritableNestedSerializerMixin.Meta):
        model = TPMActivityActionPoint
        fields = [
            'id', 'author', 'person_responsible', 'is_responsible',
            'due_date', 'status', 'description', 'comments',
        ]

    def create(self, validated_data):
        validated_data['author'] = self.get_user()
        return super(TPMActivityActionPointSerializer, self).create(validated_data)


class TPMActivityLightSerializer(TPMPermissionsBasedSerializerMixin, WritableNestedSerializerMixin,
                                 serializers.ModelSerializer):
    implementing_partner = SeparatedReadWriteField(
        read_field=PartnerOrganizationLightSerializer(read_only=True),
    )
    partnership = SeparatedReadWriteField(
        read_field=InterventionListSerializer(read_only=True),
    )

    cp_output = SeparatedReadWriteField(
        read_field=ResultSerializer(read_only=True),
        required=False,
    )

    locations = SeparatedReadWriteField(
        read_field=LocationLightSerializer(many=True, read_only=True),
    )

    pd_files = TPMActivityPDSerializer(many=True, required=False)

    action_points = TPMActivityActionPointSerializer(many=True, required=False)

    class Meta(TPMPermissionsBasedSerializerMixin.Meta, WritableNestedSerializerMixin.Meta):
        model = TPMActivity
        fields = [
            'id', 'implementing_partner', 'partnership', 'cp_output',
            'date', 'locations', 'pd_files', 'action_points',
        ]


class TPMActivitySerializer(TPMActivityLightSerializer):
    partnership = SeparatedReadWriteField(
        read_field=InterventionCreateUpdateSerializer(read_only=True),
    )

    def validate(self, attrs):
        validated_data = super(TPMActivitySerializer, self).validate(attrs)

        if '_delete' in validated_data:
            return validated_data

        if 'id' in validated_data:
            try:
                self.instance = self.Meta.model.objects.get(id=validated_data['id'])
            except self.Meta.model.DoesNotExist:
                raise ValidationError('Activity does not exist')

        implementing_partner = validated_data.get(
            'implementing_partner',
            self.instance.implementing_partner if self.instance else None
        )
        if not implementing_partner:
            raise ValidationError({'implementing_partner': self.error_messages['required']})

        if 'partnership' in validated_data:
            if not Intervention.objects.filter(
                id=validated_data['partnership'].id,
                agreement__partner_id=implementing_partner.id
            ).exists():
                raise ValidationError({
                    'partnership': self.fields['partnership'].error_messages['does_not_exist'].format(
                        pk_value=validated_data['partnership'].id
                    )
                })

        partnership = validated_data.get('partnership', self.instance.partnership if self.instance else None)
        if not partnership:
            raise ValidationError({'partnership': self.error_messages['required']})

        if validated_data.get('cp_output'):
            if not Result.objects.filter(
                id=validated_data['cp_output'].id,
                intervention_links__intervention_id=partnership.id
            ).exists():
                raise ValidationError({
                    'cp_output': self.fields['cp_output'].write_field.error_messages['does_not_exist'].format(
                        pk_value=validated_data['cp_output'].id
                    )
                })

        if 'locations' in validated_data:
            locations = set(map(lambda x: x.id, validated_data['locations']))
            diff = locations - set(Location.objects.filter(
                id__in=locations,
                intervention_sector_locations__intervention_id=partnership.id
            ).values_list('id', flat=True))

            if diff:
                raise ValidationError({
                    'locations': [
                        self.fields['locations'].write_field.child_relation.error_messages['does_not_exist'].format(
                            pk_value=pk
                        )
                        for pk in diff
                    ]
                })

        return validated_data

    class Meta(TPMActivityLightSerializer.Meta):
        pass


class TPMVisitLightSerializer(StatusPermissionsBasedRootSerializerMixin, WritableNestedSerializerMixin,
                              serializers.ModelSerializer):
    tpm_activities = TPMActivityLightSerializer(many=True, required=False)

    tpm_partner = SeparatedReadWriteField(
        read_field=TPMPartnerLightSerializer(read_only=True),
    )

    sections = SeparatedReadWriteField(
        read_field=SectionSerializer(read_only=True, many=True),
    )

    offices = SeparatedReadWriteField(
        read_field=OfficeSerializer(read_only=True, many=True)
    )

    unicef_focal_points = SeparatedReadWriteField(
        read_field=MinimalUserSerializer(read_only=True, many=True),
    )

    tpm_partner_focal_points = SeparatedReadWriteField(
        read_field=TPMPartnerStaffMemberSerializer(read_only=True, many=True),
    )

    status_date = serializers.ReadOnlyField()

    implementing_partners = serializers.SerializerMethodField()

    locations = serializers.SerializerMethodField()

    def get_implementing_partners(self, obj):
        return PartnerOrganizationLightSerializer(
            set(map(
                lambda a: a.implementing_partner,
                obj.tpm_activities.all()
            )),
            many=True
        ).data

    def get_locations(self, obj):
        return LocationLightSerializer(
            set(itertools.chain(*map(
                lambda a: a.locations.all(),
                obj.tpm_activities.all()
            ))),
            many=True
        ).data

    class Meta(StatusPermissionsBasedRootSerializerMixin.Meta, WritableNestedSerializerMixin.Meta):
        model = TPMVisit
        permission_class = TPMPermission
        fields = [
            'id', 'start_date', 'end_date',
            'tpm_activities', 'tpm_partner', 'implementing_partners', 'locations',
            'status', 'status_date', 'reference_number',
            'sections', 'offices', 'tpm_partner_focal_points', 'unicef_focal_points',
            'date_created', 'date_of_assigned', 'date_of_tpm_accepted',
            'date_of_tpm_rejected', 'date_of_tpm_reported', 'date_of_unicef_approved',
            'date_of_tpm_report_rejected', 'date_of_cancelled',
        ]


class TPMVisitSerializer(TPMVisitLightSerializer):
    tpm_activities = TPMActivitySerializer(many=True, required=False)

    attachments = TPMAttachmentsSerializer(many=True, required=False)
    report = TPMReportAttachmentsSerializer(many=True, required=False)

    report_reject_comments = TPMVisitReportRejectCommentSerializer(many=True, read_only=True)

    def validate(self, attrs):
        validated_data = super(TPMVisitSerializer, self).validate(attrs)

        tpm_partner = validated_data.get('tpm_partner', self.instance.tpm_partner if self.instance else None)

        if 'tpm_partner_focal_points' in validated_data:
            tpm_partner_focal_points = set(map(lambda x: x.id, validated_data['tpm_partner_focal_points']))
            diff = tpm_partner_focal_points - set(TPMPartnerStaffMember.objects.filter(
                id__in=tpm_partner_focal_points,
                tpm_partner_id=tpm_partner.id
            ).values_list('id', flat=True))

            if diff:
                raise ValidationError({
                    'tpm_partner_focal_points': [
                        self.fields['tpm_partner_focal_points'].write_field.child_relation
                            .error_messages['does_not_exist'].format(pk_value=pk)
                        for pk in diff
                    ]
                })

        return validated_data

    class Meta(TPMVisitLightSerializer.Meta):
        fields = TPMVisitLightSerializer.Meta.fields + [
            'reject_comment',
            'attachments',
            'report',
            'report_reject_comments',
        ]
        extra_kwargs = {
            'tpm_partner': {'required': True},
            'unicef_focal_points': {'required': True},
        }


class TPMVisitDraftSerializer(TPMVisitSerializer):
    class Meta(TPMVisitSerializer.Meta):
        extra_kwargs = {
            'tpm_partner': {'required': False},
        }
