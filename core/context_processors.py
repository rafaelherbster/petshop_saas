from django.urls import reverse
from core.models import UserProfile

def tenant_context(request):
    pet_shop = getattr(request, 'pet_shop', None)

    if not pet_shop and request.user.is_authenticated:
        profile = UserProfile.objects.filter(user=request.user).first()

        if profile and profile.pet_shop and profile.pet_shop.slug:
            pet_shop = profile.pet_shop

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
            'service_list_url': u('service_list'),  # 👈 ADICIONE ISSO
            'config_url': u('config'),
        }
    else:
        fallback = reverse('config_no_slug')

        urls = {
            'dashboard_url': fallback,
            'tutor_list_url': fallback,
            'appointment_list_url': fallback,
            'pet_list_url': fallback,
            'service_list_url': fallback,  # 👈 ADICIONE AQUI TAMBÉM
            'config_url': fallback,
        }

    return {
        'pet_shop': pet_shop,
        **urls
    }