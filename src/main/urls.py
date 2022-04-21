from django.contrib import admin
from django.urls import path, include

from main import views

urlpatterns = [
    path('methods/update-blogger/<str:blogger_login>/', views.update_blogger),
    path('fromdb/', views.from_db_view),
    path('fromdb-socials/', views.from_db_view_socials),
    path('fromdb-socials-links/', views.from_db_view_socials_links),
    path('fromdb-global/', views.from_db_view_global),
    path('all_from_db/', views.all_from_db, name='all_from_db'),
]
