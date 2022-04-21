import time

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import GlobalTopSerializer
from main.models import Blogger
from .api.social.data.ApiService import ApiService
from .api.top.general import Filter as GeneralFilter, metrics as general_metrics
from .api.top.instagram import Filter as InstagramFilter, metrics as instagram_metrics, custom_serializer
from .tasks import test_task


# Create your views here.


def test_celery_view(request):
    test_task.delay("hi")
    return JsonResponse({"success": True})


class StatisticView(APIView):
    def get(self, request, login: str):
        st = time.monotonic()
        blogger = get_object_or_404(Blogger, login=login, social_network_type_id=3)

        print('request', login)
        response = Response(ApiService.statistics(blogger))
        print('end request', login, 'time', time.monotonic() - st)
        return response


class StatisticViewLanguageSupport(APIView):
    def get(self, request, login: str, language: str):
        st = time.monotonic()
        blogger = get_object_or_404(Blogger, login=login, social_network_type_id=3)

        print('request', login)
        response = Response(ApiService.statistics_language(blogger, language))
        print('end request', login, 'time', time.monotonic() - st)
        return response


class StatisticViewLanguageSupport(APIView):
    def get(self, request, login: str, language: str):
        st = time.monotonic()
        blogger = get_object_or_404(Blogger, login=login, social_network_type_id=3)

        print('request', login)
        response = Response(ApiService.statistics_language(blogger, language))
        print('end request', login, 'time', time.monotonic() - st)
        return response


class TopBloggersView(APIView):
    def post(self, request, social_network_type_id=None):
        if social_network_type_id is None:
            results = GeneralFilter.filter(request)
            # results = self.paginate_queryset(q, request, view=self)
            serializer = GlobalTopSerializer(results, many=True)
            return Response(serializer.data)
        elif social_network_type_id == 3:
            results = InstagramFilter.filter(request)
            results = custom_serializer.instagram_serializer(results)
            return Response(results)
            # results = self.paginate_queryset(q, request, view=self)
            # serializer = GlobalTopSerializer(results, many=True)
            # return self.get_paginated_response(serializer.data)

    def get(self, request, social_network_type_id=None):
        if social_network_type_id is None:
            data = general_metrics()
            return Response(data)
        elif social_network_type_id == 3:
            data = instagram_metrics()
            return Response(data)
