from django.urls import path

from rest import views
from rest.views import test_celery_view

urlpatterns = [
    path("celery/task", test_celery_view, name="celery_task"),
    path('StatisticView/<str:login>/', views.StatisticView.as_view()),
    path('top/<int:social_network_type_id>/', views.TopBloggersView.as_view()),
    path('top/', views.TopBloggersView.as_view()),
]
