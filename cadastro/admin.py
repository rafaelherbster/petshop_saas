from django.contrib import admin
from core.admin_base import TenantModelAdmin
from .models import Tutor, Pet, LoyaltyCard


@admin.register(Tutor)
class TutorAdmin(TenantModelAdmin):
    list_display = ('name', 'phone', 'email', 'cpf', 'pet_shop')
    search_fields = ('name', 'phone', 'email', 'cpf')


@admin.register(Pet)
class PetAdmin(TenantModelAdmin):
    list_display = ('name', 'species', 'breed', 'gender', 'tutor', 'pet_shop')
    list_filter = ('species', 'gender', 'size')
    search_fields = ('name', 'tutor__name')


@admin.register(LoyaltyCard)
class LoyaltyCardAdmin(TenantModelAdmin):
    tenant_field = 'pet__pet_shop'  # LoyaltyCard não tem pet_shop direto, usa relationship
    list_display = ('pet', 'visits_count', 'max_visits', 'redeemed_at')
    list_filter = ('redeemed_at',)
