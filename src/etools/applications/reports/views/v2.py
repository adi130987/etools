import csv
import datetime
import functools
import operator

from django.db.models import Q
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_csv.renderers import CSVRenderer, JSONRenderer

from etools.applications.EquiTrack.mixins import ExportModelMixin, QueryStringFilterMixin
from etools.applications.EquiTrack.renderers import CSVFlatRenderer
from etools.applications.partners.filters import PartnerScopeFilter
from etools.applications.partners.models import Intervention
from etools.applications.partners.permissions import PartnershipManagerPermission, PartnershipManagerRepPermission
from etools.applications.reports.models import (
    AppliedIndicator,
    CountryProgramme,
    Disaggregation,
    Indicator,
    LowerResult,
    Result,
    SpecialReportingRequirement,
)
from etools.applications.reports.permissions import PMEPermission
from etools.applications.reports.serializers.exports import (
    AppliedIndicatorExportFlatSerializer,
    AppliedIndicatorExportSerializer,
    LowerResultExportFlatSerializer,
    LowerResultExportSerializer,
)
from etools.applications.reports.serializers.v1 import IndicatorSerializer
from etools.applications.reports.serializers.v2 import (
    AppliedIndicatorSerializer,
    DisaggregationSerializer,
    LowerResultSerializer,
    MinimalOutputListSerializer,
    OutputListSerializer,
    SpecialReportingRequirementSerializer,
)


class OutputListAPIView(ListAPIView):
    serializer_class = OutputListSerializer
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        """
        Use different serializers for methods
        """
        if self.request.method == "GET":
            if self.request.query_params.get("verbosity", "") == 'minimal':
                return MinimalOutputListSerializer
        return super(OutputListAPIView, self).get_serializer_class()

    def get_queryset(self):
        q = Result.outputs.all()
        query_params = self.request.query_params
        queries = []
        result_ids = []
        if query_params:
            if "year" in query_params.keys():
                cp_year = query_params.get("year", None)
                queries.append(Q(country_programme__wbs__contains='/A0/'))
                queries.append(Q(country_programme__from_date__year__lte=cp_year))
                queries.append(Q(country_programme__to_date__year__gte=cp_year))
            if "result_type" in query_params.keys():
                queries.append(Q(result_type__name=query_params.get("result_type").title()))
            if "country_programme" in query_params.keys():
                cp = query_params.get("country_programme", None)
                queries.append(Q(country_programme=cp))
            if "values" in query_params.keys():
                result_ids = query_params.get("values", None)
                try:
                    result_ids = [int(x) for x in result_ids.split(",")]
                except ValueError:
                    raise ValidationError("ID values must be integers")
                else:
                    queries.append(Q(id__in=result_ids))
        if queries:
            expression = functools.reduce(operator.and_, queries)
            q = q.filter(expression)
            # check if all value IDs passed in are returned by the query
            if result_ids and len(result_ids) != q.count():
                raise ValidationError("One of the value IDs was not found")

        if any(x in ['year', 'country_programme', 'values'] for x in query_params.keys()):
            return q
        else:
            show_all = query_params.get('show_all', None)
            if show_all in ['true', 'True']:
                return q
            current_cp = CountryProgramme.main_active()
            return q.filter(country_programme=current_cp)

    def list(self, request):
        dropdown = self.request.query_params.get("dropdown", None)
        if dropdown in ['true', 'True', '1', 'yes']:
            cp_outputs = list(self.get_queryset().values('id', 'name', 'wbs'))
            return Response(
                cp_outputs,
                status=status.HTTP_200_OK
            )
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class OutputDetailAPIView(RetrieveAPIView):
    queryset = Result.outputs.all()
    serializer_class = OutputListSerializer
    permission_classes = (IsAdminUser,)


class ResultIndicatorListAPIView(ListAPIView):
    serializer_class = IndicatorSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request, pk=None, format=None):
        """
        Return All Indicators for Result
        """
        indicators = Indicator.objects.filter(result__pk=pk)
        serializer = self.get_serializer(indicators, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class LowerResultsListAPIView(ExportModelMixin, ListAPIView):
    """
    Returns a list of LowerResults.
    """
    serializer_class = LowerResultSerializer
    permission_classes = (PartnershipManagerPermission,)
    filter_backends = (PartnerScopeFilter,)
    renderer_classes = (
        JSONRenderer,
        CSVRenderer,
        CSVFlatRenderer,
    )

    def get_serializer_class(self):
        """
        Use different serializers for methods
        """
        query_params = self.request.query_params
        if "format" in query_params.keys():
            if query_params.get("format") == 'csv':
                return LowerResultExportSerializer
            if query_params.get("format") == 'csv_flat':
                return LowerResultExportFlatSerializer
        return super(LowerResultsListAPIView, self).get_serializer_class()

    def get_queryset(self, format=None):
        q = LowerResult.objects.all()
        query_params = self.request.query_params

        if query_params:
            queries = []
            if "search" in query_params.keys():
                queries.append(
                    Q(result_link__intervention__number__icontains=query_params.get("search")) |
                    Q(name__icontains=query_params.get("search"))
                )
            if queries:
                expression = functools.reduce(operator.and_, queries)
                q = q.filter(expression)

        return q


class LowerResultsDeleteView(DestroyAPIView):
    permission_classes = (PartnershipManagerRepPermission,)

    def delete(self, request, *args, **kwargs):
        try:
            lower_result = LowerResult.objects.get(id=int(kwargs['pk']))
        except LowerResult.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if lower_result.result_link.intervention.status in [Intervention.DRAFT] or \
            request.user in lower_result.result_link.intervention.unicef_focal_points.all() or \
            request.user.groups.filter(name__in=['Partnership Manager',
                                                 'Senior Management Team']).exists():
            lower_result.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("You do not have permissions to delete a lower result")


class DisaggregationListCreateView(ListCreateAPIView):
    serializer_class = DisaggregationSerializer
    queryset = Disaggregation.objects.all()
    permission_classes = (PMEPermission, )


class DisaggregationRetrieveUpdateView(RetrieveUpdateAPIView):
    serializer_class = DisaggregationSerializer
    queryset = Disaggregation.objects.all()
    permission_classes = (PMEPermission, )


class AppliedIndicatorListAPIView(ExportModelMixin, ListAPIView):
    """
    Returns a list of AppliedIndicators.
    """
    serializer_class = AppliedIndicatorSerializer
    permission_classes = (PartnershipManagerPermission,)
    filter_backends = (PartnerScopeFilter,)
    renderer_classes = (
        JSONRenderer,
        CSVRenderer,
        CSVFlatRenderer,
    )

    def get_serializer_class(self):
        """
        Use different serializers for methods
        """
        query_params = self.request.query_params
        if "format" in query_params.keys():
            if query_params.get("format") == 'csv':
                return AppliedIndicatorExportSerializer
            if query_params.get("format") == 'csv_flat':
                return AppliedIndicatorExportFlatSerializer
        return super(AppliedIndicatorListAPIView, self).get_serializer_class()

    def get_queryset(self, format=None):
        q = AppliedIndicator.objects.all()
        query_params = self.request.query_params

        if query_params:
            queries = []
            if "search" in query_params.keys():
                queries.append(
                    Q(lower_result__result_link__intervention__number__icontains=query_params.get("search")) |
                    Q(lower_result__name__icontains=query_params.get("search")) |
                    Q(context_code__icontains=query_params.get("search"))
                )
            if queries:
                expression = functools.reduce(operator.and_, queries)
                q = q.filter(expression)

        return q


class AppliedIndicatorLocationExportView(QueryStringFilterMixin, APIView):

    def get(self, request, *args, **kwargs):

        fieldnames = {
            'partner': 'Partner Name',
            'vendor': 'Vendor',
            'int_status': 'PD / SSFA status',
            'int_start_date': 'PD / SSFA start date',
            'int_end_date': 'PD / SSFA end date',
            'country_programme': 'Country Programme',
            'int_ref': 'PD / SSFA ref',
            'int_locations': 'Locations',
            'ind_result': 'CP Output',
            'ind_lower_result': 'Lower Result',
            'ind_title': 'Indicator',
            'ind_section': 'Section',
            'ind_cluster_name': 'Cluster Name',
            'ind_baseline': 'Baseline',
            'ind_target': 'Target',
            'ind_means_of_verification': 'Means of verification',
            'ind_ram_indicators': 'RAM indicators',
            'ind_location': 'Location',
        }

        today = '{:%Y_%m_%d}'.format(datetime.date.today())
        country_code = self.request.tenant.country_short_code
        filename = f'{today}_{country_code}_Interventions'

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'

        writer = csv.DictWriter(response, fieldnames)
        writer.writerow(fieldnames)

        interventions = self.get_intervetions()

        for intervention in interventions:
            intervention_dict = {
                'partner': str(intervention.agreement.partner),
                'vendor': intervention.agreement.partner.cso_type,
                'int_status': intervention.get_status_display(),
                'int_start_date': intervention.start,
                'int_end_date': intervention.end,
                'country_programme': str(intervention.agreement.country_programme),
                'int_ref': intervention.number.replace(',', '-'),
                'int_locations': ','.join([location.name for location in intervention.flat_locations.all()])
            }

            indicators = self.get_indicators(intervention)

            if indicators.exists():
                for indicator in indicators:
                    indicator_dict = {
                        'ind_result': indicator.lower_result.result_link.cp_output,
                        'ind_lower_result': indicator.lower_result.name,
                        'ind_title': indicator.indicator.title,
                        'ind_section': indicator.section,
                        'ind_cluster_name': indicator.cluster_name,
                        'ind_baseline': indicator.baseline,
                        'ind_target': indicator.target,
                        'ind_means_of_verification': indicator.means_of_verification,
                        'ind_ram_indicators': ', '.join([
                            ri.name for ri in indicator.lower_result.result_link.ram_indicators.all()])
                    }
                    for location in indicator.locations.all():
                        locations_dict = {
                            'ind_location': location.name
                        }
                        export_dict = {**intervention_dict, **indicator_dict, **locations_dict}
                        writer.writerow(export_dict)
            else:
                writer.writerow(intervention_dict)

        return response

    def get_intervetions(self):
        qs = Intervention.objects.select_related('agreement__partner')

        if self.request.query_params:
            queries = []
            filters = (
                ('document_type', 'document_type__in'),
                ('country_programme', 'agreement__country_programme'),
                ('start', 'start__gte'),
                ('end', 'end__lte'),
                ('office', 'offices__in'),
                ('status', 'status__in'),
                ('unicef_focal_points', 'unicef_focal_points__in'),
            )

            search_terms = ['title__icontains', 'agreement__partner__name__icontains', 'number__icontains']
            queries.extend(self.filter_params(filters))
            queries.append(self.search_params(search_terms))

            if queries:
                expression = functools.reduce(operator.and_, queries)
                qs = qs.filter(expression)

        return qs

    def get_indicators(self, intervention):
        qs = AppliedIndicator.objects.select_related("indicator", "section", "lower_result").prefetch_related(
            "locations", "lower_result__result_link__cp_output", "lower_result__result_link__ram_indicators"
        ).filter(lower_result__result_link__intervention=intervention)

        if self.request.query_params:
            queries = []
            filters = (
                ('cluster', 'cluster_indicator_title__icontains'),
                ('location', 'locations__name__icontains'),
                ('sections', 'section__in'),
            )

            search_terms = ['title__icontains', 'agreement__partner__name__icontains', 'number__icontains']
            queries.extend(self.filter_params(filters))
            queries.append(self.search_params(search_terms))

            if queries:
                expression = functools.reduce(operator.and_, queries)
                qs = qs.filter(expression)

        return qs


class SpecialReportingRequirementListCreateView(ListCreateAPIView):
    serializer_class = SpecialReportingRequirementSerializer
    permission_classes = (PartnershipManagerPermission, )
    renderer_classes = (JSONRenderer, )

    def create(self, request, *args, **kwargs):
        request.data["intervention"] = kwargs.get('intervention_pk', None)
        return super().create(request, *args, **kwargs)

    def get_queryset(self, format=None):
        q = SpecialReportingRequirement.objects.filter(
            intervention=self.kwargs.get("intervention_pk")
        )
        return q


class SpecialReportingRequirementRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = SpecialReportingRequirementSerializer
    permission_classes = (PartnershipManagerPermission, )
    renderer_classes = (JSONRenderer, )
    queryset = SpecialReportingRequirement.objects.all()

    def destroy(self, request, *args, **kwargs):
        self.requirement = self.get_object()
        if self.requirement.due_date < datetime.date.today():
            raise ValidationError(
                _("Cannot delete special reporting requirements in the past.")
            )
        return super().destroy(request, *args, **kwargs)
