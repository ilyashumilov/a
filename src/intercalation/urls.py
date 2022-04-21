from django.urls import path
from .views import *

urlpatterns = [
    path('interaction',InteractionAPI.as_view())
]