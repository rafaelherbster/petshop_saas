from threading import local
from urllib import request
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import OperationalError

# Armazenamento thread-local para o tenant atual
_thread_locals = local()


class TenantMiddleware:
    """
    Middleware que extrai e valida o tenant (PetShop) do usuário autenticado.

    Funcionalidades:
    - Define request.pet_shop e armazena em thread-local para acesso pelos models
    - Valida que o PetShop existe e está ativo (is_active=True)
    - Captura race conditions (profile deletado em outra sessão) sem quebrar
    - Qualquer erro resulta em request.pet_shop = None, nunca 500
    """
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

        # 🔥 NOVO BLOCO CORRIGIDO
        path = request.path.strip('/')
        parts = path.split('/')

        public_prefixes = ['login', 'register', 'logout', 'admin', 'publico']

        if parts and parts[0] not in public_prefixes:
            if pet_shop:
                slug = parts[0]

                if slug != pet_shop.slug:
                    raise PermissionDenied("Slug inválido para este usuário")

        try:
            response = self.get_response(request)
        finally:
            if hasattr(_thread_locals, 'pet_shop'):
                delattr(_thread_locals, 'pet_shop')

        return response

    def process_request(self, request):
        shop = get_current_pet_shop()

        if shop is None or not shop.is_active:
            raise PermissionDenied("Tenant inválido")


def get_current_pet_shop():
    """Retorna o PetShop da thread atual (usado pelos managers)."""
    return getattr(_thread_locals, 'pet_shop', None)


def set_current_pet_shop(pet_shop):
    """Define o PetShop na thread atual."""
    _thread_locals.pet_shop = pet_shop
