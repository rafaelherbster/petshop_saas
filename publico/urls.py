# -*- coding: utf-8 -*-
from django.urls import path

from publico.views import schedule_view, success_view

urlpatterns = [
    path('agendar/<slug:shop_slug>/', schedule_view, name='public_schedule'),
    path('cliente/<slug:token>/', success_view, name='public_success'),
]
