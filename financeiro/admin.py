from django.contrib import admin
from core.admin_base import TenantModelAdmin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(TenantModelAdmin):
    tenant_field = 'appointment__pet_shop'  # Payment não tem pet_shop direto
    list_display = ('appointment', 'amount', 'method', 'status')
    list_filter = ('status', 'method')
    search_fields = ('appointment__pet__name', 'appointment__service__name')
