from django.urls import path
from core.views import dashboard_view, config_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('config/', config_view, name='config'),
]