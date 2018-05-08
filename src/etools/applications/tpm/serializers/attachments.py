
from django.utils.translation import ugettext as _

from etools.applications.attachments.models import FileType
from etools.applications.attachments.serializers import Base64AttachmentSerializer
from etools.applications.attachments.serializers_fields import FileTypeModelChoiceField
from etools.applications.utils.writable_serializers.serializers import WritableNestedSerializerMixin


class TPMPartnerAttachmentsSerializer(WritableNestedSerializerMixin, Base64AttachmentSerializer):
    file_type = FileTypeModelChoiceField(queryset=FileType.objects.filter(
        code="tpm_partner"), label=_('Document Type'))

    class Meta(WritableNestedSerializerMixin.Meta, Base64AttachmentSerializer.Meta):
        pass


class TPMAttachmentsSerializer(WritableNestedSerializerMixin, Base64AttachmentSerializer):
    file_type = FileTypeModelChoiceField(queryset=FileType.objects.filter(code="tpm"), label=_('Document Type'))

    class Meta(WritableNestedSerializerMixin.Meta, Base64AttachmentSerializer.Meta):
        pass


class TPMReportSerializer(WritableNestedSerializerMixin, Base64AttachmentSerializer):
    file_type = FileTypeModelChoiceField(queryset=FileType.objects.filter(code="tpm_report"), label=_('Document Type'))

    class Meta(WritableNestedSerializerMixin.Meta, Base64AttachmentSerializer.Meta):
        pass


class TPMReportAttachmentsSerializer(WritableNestedSerializerMixin, Base64AttachmentSerializer):
    file_type = FileTypeModelChoiceField(queryset=FileType.objects.filter(code='tpm_report_attachments'),
                                         label=_('Document Type'))

    class Meta(WritableNestedSerializerMixin.Meta, Base64AttachmentSerializer.Meta):
        pass