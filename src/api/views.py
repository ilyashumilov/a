# Create your views here.
import time

from drf_yasg.utils import swagger_auto_schema
from rest_framework import renderers
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from api.extra import photo_download_from_s3
from api.filters import CustomBloggerFilter,docs
from api.serializers import BloggerSerializer, RangeSerializer, SearchSerializer
from api.services import view_service
from api.services.api_service import StatisticMethods

SORTING_OPTIONS = {"engagement_rate", "-engagement_rate", "subscribers_count", "-subscribers_count"}
BEST_TIME_TYPES = {"er", 'likes', 'comments'}


class SearchView(APIView, PageNumberPagination):
    @swagger_auto_schema(
        operation_description=f"Поиск блогеров\n{docs()}",
        request_body=SearchSerializer
    )
    def post(self, request):
        q = CustomBloggerFilter.filter_v3(request)
        results = self.paginate_queryset(q, request, view=self)
        serializer = BloggerSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)


class StatisticView(APIView):

    # @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, blogger_login: str):
        st = time.monotonic()
        print('request', blogger_login)
        response = view_service.get_statistic(blogger_login)
        print('end request', blogger_login, 'time', time.monotonic() - st)
        return response


class StatisticByRange(APIView):
    @swagger_auto_schema(
        operation_description="Запрос статистики по определенным датам\nМетоды:"
                              "[ posts_months, comments_by_post, likes_by_post, best_time_to_publish ]",
        request_body=RangeSerializer
    )
    def post(self, request, blogger_login: str):
        blogger, post_query, subscribers, blogger_simple = view_service.base_data(blogger_login)
        result = StatisticMethods(post_query, blogger, subscribers, blogger_simple).function_by_name(**request.data)
        return Response(result)


@api_view(['GET'])
def best_time_view(request, blogger_login: str, type_graph: str):
    blogger, post_query, subscribers = view_service.base_data(blogger_login)
    if type_graph not in BEST_TIME_TYPES:
        return Response({"message": "Not correct type"})


class JPEGRenderer(renderers.BaseRenderer):
    media_type = 'image/jpeg'
    format = 'jpg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


@api_view(['GET'])
@renderer_classes([JPEGRenderer])
def photo_from_s3(request, photo_s3: str):
    photo = photo_download_from_s3(photo_s3)
    return Response(photo)
