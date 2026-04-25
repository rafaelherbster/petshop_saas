from django.urls import reverse
from core.models import UserProfile
from core.views import get_user_profile
import logging

logger = logging.getLogger(__name__)


def tenant_context(request):
    pet_shop = None

    try:
        pet_shop = getattr(request, 'pet_shop', None)

        if not pet_shop and request.user.is_authenticated:
            profile = get_user_profile(request.user)

            if profile and profile.pet_shop and profile.pet_shop.slug:
                pet_shop = profile.pet_shop
    except Exception as e:
        logger.error(f"Erro ao obter contexto de tenant: {e}", exc_info=True)
        pet_shop = None

    urls = {}

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
        fallback = reverse('config_no_slug')

        urls = {
            'dashboard_url': fallback,
            'tutor_list_url': fallback,
            'appointment_list_url': fallback,
            'pet_list_url': fallback,
            'service_list_url': fallback,
            'config_url': fallback,
        }

    return {
        'pet_shop': pet_shop,
        **urls
    }