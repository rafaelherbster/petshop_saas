from django.contrib import admin
from .models import PetShop, User, UserProfile, BusinessHours


@admin.register(PetShop)
class PetShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'phone', 'pix_key', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'phone', 'pix_key')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'slug', 'phone', 'address', 'is_active')
        }),
        ('PIX', {
            'fields': ('pix_key', 'pix_qr_code'),
            'description': 'Configure a chave PIX e opcionalmente faça upload do QR code do seu app bancário'
        }),
        ('Documentos', {
            'fields': ('cnpj',),
        }),
    )


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ('pet_shop', 'weekday', 'opening_time', 'closing_time')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'pet_shop')
    list_filter = ('role',)
    search_fields = ('user__email', 'pet_shop__name')


admin.site.register(User)
