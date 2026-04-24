from threading import local
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import OperationalError

# Armazenamento thread-local para o tenant atual
_thread_locals = local()


class TenantMiddleware:
    """
    Middleware que extrai e valida o tenant (PetShop) do usuário autenticado.

    Correções aplicadas:
    - Ignora path raiz ('/')
    - Remove partes vazias da URL
    - Evita quebra em rotas públicas
    - Mantém segurança do slug
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        pet_shop = None

        # 🔹 Identificação segura do tenant
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

        # 🔹 Normalização do path (corrigido)
        path = request.path.strip('/')

        # Se for raiz ("/"), deixa passar
        if not path:
            response = self.get_response(request)
            return response

        parts = path.split('/')

        public_prefixes = ['login', 'register', 'logout', 'admin', 'publico']

        # Rotas públicas passam direto
        if parts[0] in public_prefixes:
            response = self.get_response(request)
            return response

        # Se usuário não tem tenant, não bloqueia aqui
        if not pet_shop:
            response = self.get_response(request)
            return response

        slug = parts[0]

        if slug != pet_shop.slug:
            raise PermissionDenied("Slug inválido para este usuário")

        try:
            response = self.get_response(request)
        finally:
            if hasattr(_thread_locals, 'pet_shop'):
                delattr(_thread_locals, 'pet_shop')

        return response


def get_current_pet_shop():
    """Retorna o PetShop da thread atual (usado pelos managers)."""
    return getattr(_thread_locals, 'pet_shop', None)


def set_current_pet_shop(pet_shop):
    """Define o PetShop na thread atual."""
    _thread_locals.pet_shop = pet_shop