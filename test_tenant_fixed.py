import pytest
from django.core.exceptions import PermissionDenied

from core.middleware import set_current_pet_shop
from agenda.models import Appointment, Service
from cadastro.models import Tutor, Pet
from core.models import PetShop


@pytest.mark.django_db
def test_sem_tenant_levanta_permission_denied():
    set_current_pet_shop(None)

    with pytest.raises(PermissionDenied):
        list(Appointment.objects.all())


@pytest.mark.django_db
def test_tenant_ativo_retorna_dados_corretos():
    shop = PetShop.objects.create(name="Shop A", phone="111", is_active=True)

    # Define tenant antes de criar objetos
    set_current_pet_shop(shop)

    tutor = Tutor.objects.create(name="T1", phone="222", pet_shop=shop)
    pet = Pet.objects.create(name="Pet1", tutor=tutor, species='dog', gender='M')
    service = Service.objects.create(
        name="Banho",
        price=30.0,
        duration_minutes=30,
        pet_shop=shop
    )

    Appointment.objects.create(
        pet=pet,
        date='2026-01-01',
        time='10:00',
        service=service
    )

    qs = Appointment.objects.all()

    assert qs.count() == 1
    assert qs.first().pet_shop_id == shop.id


@pytest.mark.django_db
def test_tenant_inativo_bloqueia():
    shop = PetShop.objects.create(name="Shop A", phone="111", is_active=True)
    shop_inactive = PetShop.objects.create(name="Inativo", phone="333", is_active=False)

    set_current_pet_shop(shop)

    tutor = Tutor.objects.create(name="T1", phone="222", pet_shop=shop)
    pet = Pet.objects.create(name="Pet1", tutor=tutor, species='dog', gender='M')

    service = Service.objects.create(
        name="Banho",
        price=30.0,
        duration_minutes=30,
        pet_shop=shop
    )

    Appointment.objects.create(
        pet=pet,
        date='2026-01-01',
        time='10:00',
        service=service
    )

    # muda para tenant inativo
    set_current_pet_shop(shop_inactive)

    # 🔥 comportamento correto: BLOQUEAR
    with pytest.raises(PermissionDenied):
        Appointment.objects.count()


@pytest.mark.django_db
def test_criacao_appointment_define_petshop_automatico():
    shop = PetShop.objects.create(name="Shop A", phone="111", is_active=True)
    set_current_pet_shop(shop)

    tutor = Tutor.objects.create(name="T2", phone="444", pet_shop=shop)
    pet = Pet.objects.create(name="Pet2", tutor=tutor, species='cat', gender='F')

    service = Service.objects.create(
        name="Banho",
        price=30.0,
        duration_minutes=30,
        pet_shop=shop
    )

    appt = Appointment.objects.create(
        pet=pet,
        date='2026-01-02',
        time='11:00',
        service=service
    )

    assert appt.pet_shop_id == shop.id


@pytest.mark.django_db
def test_order_by_nao_quebra_filtro_tenant():
    shop = PetShop.objects.create(name="Shop A", phone="111", is_active=True)
    set_current_pet_shop(shop)

    tutor = Tutor.objects.create(name="T3", phone="555", pet_shop=shop)
    pet = Pet.objects.create(name="Pet3", tutor=tutor, species='dog', gender='M')

    service = Service.objects.create(
        name="Banho",
        price=30.0,
        duration_minutes=30,
        pet_shop=shop
    )

    Appointment.objects.create(
        pet=pet,
        date='2026-01-01',
        time='10:00',
        service=service
    )

    Appointment.objects.create(
        pet=pet,
        date='2026-01-02',
        time='11:00',
        service=service
    )

    qs = Appointment.objects.order_by('-date')

    assert all(a.pet_shop_id == shop.id for a in qs)

@pytest.mark.django_db
def test_raw_bloqueado():
    with pytest.raises(PermissionDenied):
        list(Appointment.objects.raw("SELECT * FROM agenda_appointment"))

@pytest.mark.django_db
def test_extra_bloqueado():
    with pytest.raises(PermissionDenied):
        list(Appointment.objects.extra(where=["1=1"]))