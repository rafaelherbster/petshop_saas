from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


def tenant_context(request):
    """Context processor que fornece informações do tenant para os templates.

    Este roda em TODAS as páginas, então precisa ser muito robusto.
    """
    pet_shop = None

    try:
        # ✅ Verificar se usuário está autenticado
        if not request.user.is_authenticated:
            # Usuário não logado = sem tenant
            return {
                'pet_shop': None,
                'dashboard_url': reverse('home'),
                'tutor_list_url': reverse('login'),
                'appointment_list_url': reverse('login'),
                'pet_list_url': reverse('login'),
                'service_list_url': reverse('login'),
                'config_url': reverse('login'),
            }

        # ✅ Usuário logado - tentar obter profile de forma segura
        try:
            from core.models import UserProfile
            profile = UserProfile.objects.select_related('pet_shop').filter(
                user=request.user
            ).first()

            if profile and profile.pet_shop and profile.pet_shop.is_active:
                pet_shop = profile.pet_shop
        except Exception as e:
            # Se falhar (banco vazio, etc), retorna contexto vazio
            logger.debug(f"Context processor: erro ao obter profile: {e}")
            pass

    except Exception as e:
        logger.debug(f"Context processor: erro geral: {e}")
        pass

    # ✅ Se não tem pet_shop, redirecionar para config ou login
    if pet_shop:
        slug = pet_shop.slug

        def u(name):
            return reverse(name, kwargs={'slug': slug})

        urls = {
            'dashboard_url': u('dashboard'),
            'tutor_list_url': u('tutor_list'),
            'appointment_list_url': u('appointment_list'),
            'pet_list_url': u('pet_list'),
            'service_list_url': u('service_list'),
            'config_url': u('config'),
        }
    else:
        # Usuário logado mas sem pet_shop = vai para config
        try:
            config_url = reverse('config_no_slug')
        except:
            config_url = '/config/'

        urls = {
            'dashboard_url': config_url,
            'tutor_list_url': config_url,
            'appointment_list_url': config_url,
            'pet_list_url': config_url,
            'service_list_url': config_url,
            'config_url': config_url,
        }

    return {
        'pet_shop': pet_shop,
        **urls
    }