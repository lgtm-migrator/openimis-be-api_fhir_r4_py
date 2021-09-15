from claim.models import ClaimAdmin
from core.models import Officer

from rest_framework.request import Request

from api_fhir_r4.mixins import MultiIdentifierRetrieveManySerializersMixin, MultiIdentifierRetrieverMixin
from api_fhir_r4.model_retrievers import UUIDIdentifierModelRetriever, CodeIdentifierModelRetriever

from api_fhir_r4.multiserializer import modelViewset

from api_fhir_r4.permissions import FHIRApiPractitionerPermissions
from api_fhir_r4.serializers import ClaimAdminPractitionerSerializer, EnrolmentOfficerPractitionerSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView, BaseMultiserializerFHIRView


class PractitionerViewSet(BaseMultiserializerFHIRView,
                          modelViewset.MultiSerializerModelViewSet,
                          MultiIdentifierRetrieveManySerializersMixin, MultiIdentifierRetrieverMixin):
    retrievers = [UUIDIdentifierModelRetriever, CodeIdentifierModelRetriever]
    permission_classes = (FHIRApiPractitionerPermissions,)

    lookup_field = 'identifier'

    @property
    def serializers(self):
        return {
            ClaimAdminPractitionerSerializer: (self._ca_queryset(), self._ca_serializer_validator),
            EnrolmentOfficerPractitionerSerializer: (self._eo_queryset(), self._eo_serializer_validator),
        }

    @classmethod
    def _ca_serializer_validator(cls, context):
        return cls._base_request_validator_dispatcher(
            request=context['request'],
            get_check=lambda x: cls._get_type_from_query(x) in ('prov', None),
            post_check=lambda x: cls._get_type_from_body(x) == 'prov',
            put_check=lambda x: cls._get_type_from_body(x) in ('prov', None),
        )

    @classmethod
    def _eo_serializer_validator(cls, context):
        return cls._base_request_validator_dispatcher(
            request=context['request'],
            get_check=lambda x: cls._get_type_from_query(x) in ('bus', None),
            post_check=lambda x: cls._get_type_from_body(x) == 'bus',
            put_check=lambda x: cls._get_type_from_body(x) in ('bus', None),
        )

    @classmethod
    def _base_request_validator_dispatcher(cls, request: Request, get_check, post_check, put_check):
        if request.method == 'GET':
            return get_check(request)
        elif request.method == 'POST':
            return post_check(request)
        elif request.method == 'PUT':
            return put_check(request)
        return True

    def list(self, request, *args, **kwargs):
        identifier = request.GET.get("code")
        if identifier:
            return self.retrieve(request, *args, **{**kwargs, 'identifier': identifier})
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return ClaimAdmin.objects

    def _ca_queryset(self):
        return ClaimAdmin.objects.filter(validity_to__isnull=True).order_by('validity_from')

    def _eo_queryset(self):
        return Officer.objects.filter(validity_to__isnull=True).order_by('validity_from')

    @classmethod
    def _get_type_from_body(cls, request):
        try:
            # See: http://hl7.org/fhir/R4/organization.html
            return request.data['type'][0]['coding'][0]['code'].lower()
        except KeyError:
            return None

    @classmethod
    def _get_type_from_query(cls, request):
        try:
            return request.GET['resourceType'].lower()
        except KeyError:
            return None
