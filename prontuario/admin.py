from django.contrib import admin
from core.admin_base import TenantModelAdmin
from .models import HealthRecord


@admin.register(HealthRecord)
class HealthRecordAdmin(TenantModelAdmin):
    list_display = ('pet', 'date', 'type', 'next_due', 'pet_shop')
    list_filter = ('type', 'date')
    search_fields = ('pet__name', 'description')
    date_hierarchy = 'date'
