
from rest_framework.metadata import SimpleMetadata

from etools.applications.attachments.metadata import ModelChoiceFieldMixin
from etools.applications.permissions2.metadata import PermittedFSMTransitionActionMetadataMixin
from etools.applications.utils.common.metadata import (CRUActionsMetadataMixin, ReadOnlyFieldWithChoicesMixin,
                                                       SeparatedReadWriteFieldMetadata,)
from etools.applications.utils.permissions.metadata import PermissionsBasedMetadataMixin


class TPMBaseMetadata(
    ReadOnlyFieldWithChoicesMixin,
    ModelChoiceFieldMixin,
    SeparatedReadWriteFieldMetadata,
    CRUActionsMetadataMixin,
    SimpleMetadata
):
    pass


class TPMPermissionBasedMetadata(
    PermittedFSMTransitionActionMetadataMixin,
    PermissionsBasedMetadataMixin,
    TPMBaseMetadata
):
    def get_serializer_info(self, serializer):
        if serializer.instance:
            serializer.context['instance'] = serializer.instance
        return super(TPMPermissionBasedMetadata, self).get_serializer_info(serializer)
