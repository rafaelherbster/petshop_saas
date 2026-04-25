from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from core.decorators import tenant_required
from core.models import PetShop, UserProfile
from django.utils.text import slugify

User = get_user_model()

# =========================
# HOME / LANDING PAGE
# =========================
def home_view(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile and profile.pet_shop and profile.pet_shop.is_active:
            return redirect('dashboard', slug=profile.pet_shop.slug)
        return redirect('config_no_slug')
    return render(request, 'core/home.html')

# =========================
# LOGIN
# =========================
def login_view(request):

    if request.user.is_authenticated:
        profile = UserProfile.objects.filter(user=request.user).first()

        if profile and profile.pet_shop and profile.pet_shop.is_active:
            return redirect('dashboard', slug=profile.pet_shop.slug)

        return redirect('config_no_slug')

    error = None

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)

            profile = UserProfile.objects.filter(user=user).first()

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


# =========================
# REGISTER (CRIA USUÁRIO E PETSHOP)
# =========================
def register_view(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile and profile.pet_shop:
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
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
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
                            username=email.split('@')[0],
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
                        return redirect('dashboard', slug=shop.slug)
                    except Exception as e:
                        import logging
                        logging.error(f"Erro ao criar conta: {e}")
                        error = 'Erro ao criar conta. Tente novamente.'

    return render(request, 'core/register.html', {'error': error})


# =========================
# CONFIG SEM SLUG (ONBOARDING)
# =========================
@login_required
def config_view_no_slug(request):
    profile = UserProfile.objects.filter(user=request.user).first()

    if profile and profile.pet_shop:
        return redirect('config', slug=profile.pet_shop.slug)

    if request.method == 'POST':
        name = request.POST.get('name')

        slug = slugify(name)

        # evita slug duplicado
        if PetShop.objects.filter(slug=slug).exists():
            return render(request, 'core/config.html', {
                'error': 'Nome do petshop já está em uso'
            })

        shop = PetShop.objects.create(
            name=name,
            slug=slug,
            phone=request.POST.get('phone'),
            address=request.POST.get('address', ''),
            cnpj=request.POST.get('cnpj', ''),
            pix_key=request.POST.get('pix_key', '') or None,
            is_active=True
        )

        profile.pet_shop = shop
        profile.role = 'owner'
        profile.save()

        return redirect('dashboard', slug=shop.slug)

    return render(request, 'core/config.html')


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

    if request.method == 'POST':
        pet_shop.name = request.POST.get('name')
        pet_shop.phone = request.POST.get('phone')
        pet_shop.address = request.POST.get('address', '')
        pet_shop.cnpj = request.POST.get('cnpj', '')
        pet_shop.pix_key = request.POST.get('pix_key', '') or None
        pet_shop.save()

        return redirect('dashboard', slug=pet_shop.slug)

    return render(request, 'core/config.html', {'pet_shop': pet_shop})


# =========================
# DASHBOARD
# =========================
@tenant_required
@login_required
def dashboard_view(request, slug):
    pet_shop = request.pet_shop

    if not pet_shop:
        from django.contrib import messages
        messages.warning(request, 'Complete o cadastro do seu Pet Shop para começar.')
        return redirect('config', slug=slug)

    from agenda.models import Appointment
    from financeiro.models import Payment
    from prontuario.models import HealthRecord
    from cadastro.models import Pet

    from django.db.models import Sum
    from datetime import date, datetime
    from django.utils import timezone

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

    now_time = timezone.localtime(timezone.now())
    hour = now_time.hour

    if hour < 12:
        greeting = 'Bom dia!'
    elif hour < 18:
        greeting = 'Boa tarde!'
    else:
        greeting = 'Boa noite!'

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