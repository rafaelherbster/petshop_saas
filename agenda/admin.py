from django.contrib import admin
from core.admin_base import TenantModelAdmin
from .models import Appointment, Service


@admin.register(Service)
class ServiceAdmin(TenantModelAdmin):
    list_display = ('name', 'price', 'duration_minutes', 'is_active', 'pet_shop')
    list_filter = ('is_active',)
    search_fields = ('name', 'price')


@admin.register(Appointment)
class AppointmentAdmin(TenantModelAdmin):
    list_display = ('pet', 'service', 'date', 'time', 'status', 'pet_shop')
    list_filter = ('status', 'date')
    search_fields = ('pet__name', 'service__name')
    date_hierarchy = 'date'
