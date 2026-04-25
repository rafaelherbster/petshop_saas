from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages
from core.decorators import tenant_required
from core.models import PetShop, UserProfile
from agenda.models import Appointment
from financeiro.models import Payment
from prontuario.models import HealthRecord
from cadastro.models import Pet
from django.utils.text import slugify
from datetime import date, datetime
import logging
import sys

logger = logging.getLogger(__name__)

# Adiciona handler de console para garantir logs em produção
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(levelname)s %(asctime)s %(module)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

User = get_user_model()


# =========================
# HELPER FUNCTIONS
# =========================
def get_user_profile(user):
    """Obter o perfil do usuário de forma reutilizável"""
    return UserProfile.objects.filter(user=user).first()


def get_greeting_message(hour=None):
    """Retorna mensagem de saudação baseada na hora"""
    if hour is None:
        now_time = timezone.localtime(timezone.now())
        hour = now_time.hour
    
    if hour < 12:
        return 'Bom dia!'
    elif hour < 18:
        return 'Boa tarde!'
    else:
        return 'Boa noite!'


# =========================
# HOME / LANDING PAGE
# =========================
def home_view(request):
    if request.user.is_authenticated:
        profile = get_user_profile(request.user)
        if profile and profile.pet_shop and profile.pet_shop.is_active:
            return redirect('dashboard', slug=profile.pet_shop.slug)
        return redirect('config_no_slug')
    return render(request, 'core/home.html')

# =========================
# LOGIN
# =========================
def login_view(request):
    try:
        if request.user.is_authenticated:
            profile = get_user_profile(request.user)
            if profile and profile.pet_shop and profile.pet_shop.is_active:
                return redirect('dashboard', slug=profile.pet_shop.slug)
            return redirect('config_no_slug')

        error = None

        if request.method == 'POST':
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')

            if not email or not password:
                error = 'Preencha email e senha'
            else:
                try:
                    validate_email(email)
                except ValidationError:
                    error = 'Email inválido'

                if not error:
                    user = authenticate(request, username=email, password=password)
                    if user:
                        login(request, user)
                        profile = get_user_profile(user)
                        if not profile or not profile.pet_shop or not profile.pet_shop.is_active:
                            logout(request)
                            error = 'Petshop inválido ou inativo'
                        else:
                            slug = profile.pet_shop.slug
                            next_url = request.GET.get('next')
                            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
                                return redirect(next_url)
                            return redirect('dashboard', slug=slug)
                    else:
                        error = 'Credenciais inválidas'

        return render(request, 'core/login.html', {'error': error})
    except Exception as e:
        logger.error(f"Erro no login_view: {e}", exc_info=True)
        return render(request, 'core/login.html', {'error': 'Erro interno. Tente novamente.'})


# =========================
# REGISTER (CRIA USUÁRIO E PETSHOP)
# =========================
@transaction.atomic()
def register_view(request):
    # Primeiro verifica se usuário já está logado
    if request.user.is_authenticated:
        profile = get_user_profile(request.user)
        if profile and profile.pet_shop and profile.pet_shop.is_active:
            return redirect('dashboard', slug=profile.pet_shop.slug)
        return redirect('config_no_slug')

    error = None

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        shop_name = request.POST.get('shop_name', '').strip()
        shop_phone = request.POST.get('shop_phone', '').strip()

        if not email or not password or not shop_name:
            error = 'Preencha todos os campos obrigatórios'
        else:
            try:
                validate_email(email)
            except ValidationError:
                error = 'Email inválido'

            if not error:
                if password != confirm_password:
                    error = 'As senhas não conferem'
                elif len(password) < 6:
                    error = 'A senha deve ter pelo menos 6 caracteres'
                elif User.objects.filter(email=email).exists():
                    error = 'Email já cadastrado'
                else:
                    try:
                        user = User.objects.create_user(
                            username=email,
                            email=email,
                            password=password
                        )
                        slug = slugify(shop_name)
                        if PetShop.objects.filter(slug=slug).exists():
                            slug = f"{slug}-{user.id}"
                        shop = PetShop.objects.create(
                            name=shop_name,
                            slug=slug,
                            phone=shop_phone or '',
                            is_active=True
                        )
                        profile = user.profile
                        profile.pet_shop = shop
                        profile.role = 'owner'
                        profile.save()
                        login(request, user)
                        messages.success(request, f'Conta criada com sucesso! Bem-vindo ao {shop.name}')
                        return redirect('dashboard', slug=shop.slug)
                    except Exception as e:
                        logger.error(f"Erro ao criar conta: {e}", exc_info=True)
                        error = 'Erro ao criar conta. Tente novamente.'

    return render(request, 'core/register.html', {'error': error})


# =========================
# CONFIG SEM SLUG (ONBOARDING)
# =========================
@login_required
@transaction.atomic()
def config_view_no_slug(request):
    profile = get_user_profile(request.user)

    if profile and profile.pet_shop:
        return redirect('config', slug=profile.pet_shop.slug)

    error = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not name:
            error = 'Nome do petshop é obrigatório'
        else:
            try:
                slug = slugify(name)

                # Se slug duplicado, adiciona user.id como no register_view
                if PetShop.objects.filter(slug=slug).exists():
                    slug = f"{slug}-{request.user.id}"

                shop = PetShop.objects.create(
                    name=name,
                    slug=slug,
                    phone=phone or '',
                    address=request.POST.get('address', ''),
                    cnpj=request.POST.get('cnpj', ''),
                    pix_key=request.POST.get('pix_key', '') or None,
                    is_active=True
                )

                profile.pet_shop = shop
                profile.role = 'owner'
                profile.save()

                messages.success(request, f'Pet Shop {shop.name} criado com sucesso!')
                return redirect('dashboard', slug=shop.slug)
            except Exception as e:
                logger.error(f"Erro ao criar petshop: {e}", exc_info=True)
                error = 'Erro ao criar petshop. Tente novamente.'

    return render(request, 'core/config.html', {'error': error})


# =========================
# LOGOUT (CORRIGIDO)
# =========================
@login_required
def logout_view(request):
    logout(request)

    response = redirect('login')

    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


# =========================
# CONFIG COM SLUG
# =========================
@tenant_required
@login_required
def config_view(request, slug):
    pet_shop = request.pet_shop
    error = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        
        if not name:
            error = 'Nome do petshop é obrigatório'
        else:
            try:
                pet_shop.name = name
                pet_shop.phone = request.POST.get('phone', '').strip()
                pet_shop.address = request.POST.get('address', '')
                pet_shop.cnpj = request.POST.get('cnpj', '')
                pet_shop.pix_key = request.POST.get('pix_key', '') or None
                pet_shop.save()

                messages.success(request, 'Configurações atualizadas com sucesso!')
                return redirect('dashboard', slug=pet_shop.slug)
            except Exception as e:
                logger.error(f"Erro ao atualizar petshop: {e}", exc_info=True)
                error = 'Erro ao atualizar petshop. Tente novamente.'

    return render(request, 'core/config.html', {'pet_shop': pet_shop, 'error': error})


# =========================
# DASHBOARD
# =========================
@tenant_required
@login_required
def dashboard_view(request, slug):
    pet_shop = request.pet_shop

    if not pet_shop:
        messages.warning(request, 'Complete o cadastro do seu Pet Shop para começar.')
        return redirect('config', slug=slug)

    today = date.today()

    today_appointments = Appointment.objects.filter(
        pet_shop=pet_shop,
        date=today,
    )

    start_of_month = datetime(today.year, today.month, 1)

    month_payments = Payment.objects.filter(
        appointment__pet_shop=pet_shop,
        created_at__gte=start_of_month,
        status='paid',
    ).aggregate(total=Sum('amount'))

    upcoming_vaccines = HealthRecord.objects.filter(
        pet__pet_shop=pet_shop,
        type='vacina',
        next_due__isnull=False,
    ).exclude(next_due__lt=today)[:5]

    birthday_pets = Pet.objects.filter(
        pet_shop=pet_shop,
        birth_date__month=today.month,
        birth_date__day=today.day,
    )

    greeting = get_greeting_message()

    context = {
        'pet_shop': pet_shop,
        'today_appointments': today_appointments,
        'today_count': today_appointments.count(),
        'pending_count': today_appointments.filter(status='agendado').count(),
        'month_revenue': month_payments['total'] or 0,
        'upcoming_vaccines': upcoming_vaccines,
        'birthday_pets': birthday_pets,
        'appointments_needing_payment': Appointment.objects.filter(
            pet_shop=pet_shop,
            status='atendido',
            payment__isnull=True,
        ).count(),
        'greeting': greeting,
    }

    return render(request, 'core/dashboard.html', context)