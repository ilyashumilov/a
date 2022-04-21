from django.contrib import admin
from django.urls import path, include, re_path

from api import views
from rest import views as viewsq
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path('search/', views.SearchView.as_view()),
    # path('statistic/<str:blogger_login>/', views.StatisticView.as_view()),
    path('statistic/<str:login>/<str:language>/', viewsq.StatisticViewLanguageSupport.as_view()),
    path('statistic/<str:login>/', viewsq.StatisticView.as_view()),

    path('statistic-range/<str:blogger_login>/', views.StatisticByRange.as_view()),

    path('best-time/<str:blogger_login>/<str:type_graph>/', views.best_time_view),

    path('photo/<photo_s3>/', views.photo_from_s3),

    re_path("swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

]
