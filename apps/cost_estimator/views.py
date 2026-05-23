import django
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from apps.build_assistant.models import Layout
from .models import MaterialPrice, LabourRate, CostEstimate, TCOProjection
from .serializers import (
    CostEstimateInputSerializer,
    CostEstimateSerializer,
    TCOInputSerializer,
    TCOProjectionSerializer,
    MaterialPriceSerializer,
    LabourRateSerializer,
)
from .services.cost_calculator import calculate_cost
from .services.tco_calculator import project_tco
from .services.pdf_generator import generate_report
from .services import cache_layer


class EstimateCostView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cost Estimator'],
        summary='Calculate upfront construction cost for a layout',
        description=(
            'Accepts a layout ID, country, and optional city. '
            'Returns a total cost and itemised breakdown using current market rates. '
            'Results are cached for 60 s; posting a material swap invalidates the cache.'
        ),
        request=CostEstimateInputSerializer,
        responses={200: CostEstimateSerializer},
        examples=[
            OpenApiExample(
                'Lagos estimate',
                value={'layout_id': 'uuid-here', 'country': 'NG', 'city': 'Lagos'},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        ser = CostEstimateInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        cached = cache_layer.get_estimate(
            str(d['layout_id']), d['country'], d['city'], d['labour_zone'],
        )
        if cached:
            return Response(cached)

        try:
            result = calculate_cost(
                str(d['layout_id']), d['country'], d['city'], d['labour_zone'],
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

        estimate = CostEstimate.objects.create(
            layout_id=d['layout_id'],
            user=request.user,
            country=d['country'],
            city=d['city'],
            total_cost=result['total_cost'],
            currency=result['currency'],
            breakdown=result['breakdown'],
        )

        payload = CostEstimateSerializer(estimate).data
        payload['disclaimer'] = result.get('disclaimer')

        cache_layer.set_estimate(
            str(d['layout_id']), d['country'], d['city'], d['labour_zone'], payload,
        )
        return Response(payload)


class TCOProjectionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cost Estimator'],
        summary='Calculate 5-year (or N-year) Total Cost of Ownership projection',
        description=(
            'Returns electricity, water, and maintenance savings over the '
            'projection period, plus payback period in months.'
        ),
        request=TCOInputSerializer,
        responses={200: TCOProjectionSerializer},
    )
    def post(self, request):
        ser = TCOInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        cached = cache_layer.get_tco(str(d['layout_id']), d['country'], d['projection_years'])
        if cached:
            return Response(cached)

        latest_estimate = CostEstimate.objects.filter(
            layout_id=d['layout_id'], user=request.user,
        ).order_by('-created_at').first()
        upfront_cost = float(latest_estimate.total_cost) if latest_estimate else 0.0

        try:
            result = project_tco(str(d['layout_id']), d['country'], upfront_cost, d['projection_years'])
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

        proj = TCOProjection.objects.create(
            layout_id=d['layout_id'],
            user=request.user,
            upfront_cost=result['upfront_cost'],
            currency=result['currency'],
            projection_years=result['projection_years'],
            annual_savings=result['annual_savings'],
            total_savings=result['total_savings'],
            payback_months=result['payback_months'],
            savings_breakdown=result['savings_breakdown'],
        )

        payload = TCOProjectionSerializer(proj).data
        cache_layer.set_tco(str(d['layout_id']), d['country'], d['projection_years'], payload)
        return Response(payload)


class PricingMaterialsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cost Estimator'],
        summary='List current material market rates',
        description='Filtered by ?country=NG&city=Lagos&category=wall. Falls back to national when city absent.',
        parameters=[
            OpenApiParameter('country', OpenApiTypes.STR, description='ISO-2 country code'),
            OpenApiParameter('city', OpenApiTypes.STR, required=False),
            OpenApiParameter('category', OpenApiTypes.STR, required=False,
                             description='wall | foundation | roof | floor | window | insulation | finishing'),
        ],
        responses={200: MaterialPriceSerializer(many=True)},
    )
    def get(self, request):
        qs = MaterialPrice.objects.all()
        country = request.query_params.get('country')
        city = request.query_params.get('city')
        category = request.query_params.get('category')

        if country:
            qs = qs.filter(country=country.upper())
        if city:
            qs = qs.filter(city__iexact=city)
        if category:
            qs = qs.filter(category=category.lower())

        return Response(MaterialPriceSerializer(qs, many=True).data)


class PricingLabourView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cost Estimator'],
        summary='List labour rate bands by skill type and region',
        parameters=[
            OpenApiParameter('country', OpenApiTypes.STR, description='ISO-2 country code'),
            OpenApiParameter('city', OpenApiTypes.STR, required=False),
            OpenApiParameter('skill_type', OpenApiTypes.STR, required=False,
                             description='mason | carpenter | plumber | electrician | labourer'),
        ],
        responses={200: LabourRateSerializer(many=True)},
    )
    def get(self, request):
        qs = LabourRate.objects.all()
        country = request.query_params.get('country')
        city = request.query_params.get('city')
        skill = request.query_params.get('skill_type')

        if country:
            qs = qs.filter(country=country.upper())
        if city:
            qs = qs.filter(city__iexact=city)
        if skill:
            qs = qs.filter(skill_type=skill.lower())

        return Response(LabourRateSerializer(qs, many=True).data)


class CostReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cost Estimator'],
        summary='Generate PDF cost report for a layout',
        description=(
            'Returns a PDF binary. Uses the most recent cost estimate and TCO '
            'projection for the layout. Pass ?country=NG to target specific pricing.'
        ),
        parameters=[
            OpenApiParameter('country', OpenApiTypes.STR, required=False, default='NG'),
        ],
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request, layout_id):
        layout = get_object_or_404(Layout, id=layout_id, user=request.user)
        country = request.query_params.get('country', 'NG').upper()

        estimate_obj = CostEstimate.objects.filter(
            layout_id=layout_id, user=request.user,
        ).order_by('-created_at').first()

        if not estimate_obj:
            try:
                est_data = calculate_cost(str(layout_id), country, '', country)
            except ValueError as e:
                return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
            estimate_obj = CostEstimate.objects.create(
                layout_id=layout_id,
                user=request.user,
                country=country,
                total_cost=est_data['total_cost'],
                currency=est_data['currency'],
                breakdown=est_data['breakdown'],
            )

        estimate_dict = CostEstimateSerializer(estimate_obj).data
        estimate_dict['country'] = estimate_obj.country

        tco_obj = TCOProjection.objects.filter(
            layout_id=layout_id, user=request.user,
        ).order_by('-created_at').first()

        if not tco_obj:
            tco_data = project_tco(str(layout_id), country, float(estimate_obj.total_cost))
            tco_obj = TCOProjection.objects.create(
                layout_id=layout_id,
                user=request.user,
                upfront_cost=tco_data['upfront_cost'],
                currency=tco_data['currency'],
                projection_years=tco_data['projection_years'],
                annual_savings=tco_data['annual_savings'],
                total_savings=tco_data['total_savings'],
                payback_months=tco_data['payback_months'],
                savings_breakdown=tco_data['savings_breakdown'],
            )

        tco_dict = TCOProjectionSerializer(tco_obj).data

        pdf_bytes = generate_report(layout, estimate_dict, tco_dict)

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ecochain_report_{layout_id}.pdf"'
        return response
