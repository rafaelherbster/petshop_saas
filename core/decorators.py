from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def tenant_required(view_func):
    def _wrapped_view(request, slug, *args, **kwargs):
        pet_shop = getattr(request, 'pet_shop', None)

        if not pet_shop:
            return redirect('/login/')

        if not pet_shop.is_active:
            raise PermissionDenied("Tenant inativo")

        if pet_shop.slug != slug:
            raise PermissionDenied("Acesso inválido ao tenant")

        return view_func(request, slug, *args, **kwargs)

    return _wrapped_view