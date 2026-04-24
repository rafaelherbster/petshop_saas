from threading import local
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import OperationalError

_thread_locals = local()


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        pet_shop = None

        try:
            if request.user.is_authenticated:
                try:
                    profile = request.user.profile
                    if profile and profile.pet_shop_id:
                        pet_shop = profile.pet_shop

                        if not (pet_shop and pet_shop.is_active):
                            pet_shop = None
                except (ObjectDoesNotExist, AttributeError, OperationalError):
                    pet_shop = None
        except Exception:
            pet_shop = None

        request.pet_shop = pet_shop
        _thread_locals.pet_shop = pet_shop

        try:
            path = request.path.strip('/')

            # ✅ Libera raiz
            if not path:
                return self.get_response(request)

            parts = path.split('/')

            public_prefixes = ['login', 'register', 'logout', 'admin', 'publico', 'password-reset']

            # ✅ Libera rotas públicas
            if parts[0] in public_prefixes:
                return self.get_response(request)

            # ✅ Usuário sem tenant → não bloqueia
            if not pet_shop:
                return self.get_response(request)

            slug = parts[0]

            # ✅ Validação de tenant
            if slug != pet_shop.slug:
                raise PermissionDenied("Slug inválido")

            return self.get_response(request)

        finally:
            if hasattr(_thread_locals, 'pet_shop'):
                delattr(_thread_locals, 'pet_shop')


def get_current_pet_shop():
    return getattr(_thread_locals, 'pet_shop', None)


def set_current_pet_shop(pet_shop):
    _thread_locals.pet_shop = pet_shop