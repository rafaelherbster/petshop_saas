"""
Admin base com suporte a multi-tenant.
Todos os ModelAdmins que herdam de TenantModelAdmin filtram automaticamente
por request.pet_shop.
"""
from django.contrib import admin


class TenantModelAdmin(admin.ModelAdmin):
    """
    ModelAdmin que filtra automaticamente por tenant (pet_shop) na listagem.

    Comportamento:
    - Superusuários e staff veem TODOS os registros (sem filtro)
    - Usuários normais: filtrados por request.pet_shop
    - Sem tenant → queryset vazio
    """
    tenant_field = 'pet_shop'  # campo ou relacionamento para filtrar (ex: 'pet__pet_shop')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Staff / superuser podem ver tudo no admin
        if request.user.is_staff or request.user.is_superuser:
            return qs
        if request.user.is_authenticated and hasattr(request, 'pet_shop') and request.pet_shop:
            filter_kwargs = {self.tenant_field: request.pet_shop}
            return qs.filter(**filter_kwargs)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change:
            # Auto-assign pet_shop para models com campo direto
            if hasattr(obj, 'pet_shop') and not obj.pet_shop_id:
                if request.user.is_authenticated and hasattr(request, 'pet_shop') and request.pet_shop:
                    obj.pet_shop = request.pet_shop
            # Ou extrai do relacionamento (ex: Payment → appointment.pet.pet_shop)
            elif hasattr(obj, 'pet') and hasattr(obj.pet, 'pet_shop') and not getattr(obj, 'pet_shop', None):
                obj.pet_shop = obj.pet.pet_shop
        super().save_model(request, obj, form, change)

