import pytest
from django.core.exceptions import PermissionDenied
from core.middleware import set_current_pet_shop
from agenda.models import Appointment, Service
from cadastro.models import Tutor, Pet
from core.models import PetShop


@pytest.mark.django_db
def test_sem_tenant_levanta_erro():
    set_current_pet_shop(None)

    with pytest.raises(PermissionDenied):
        list(Appointment.objects.all())


@pytest.mark.django_db
def test_tenant_ativo_retorna_so_seus_dados():
    shop = PetShop.objects.create(name="Shop A", phone="111", is_active=True)
    set_current_pet_shop(shop)
    tutor = Tutor.objects.create(name="T1", phone="222", pet_shop=shop)
    pet = Pet.objects.create(name="Pet1", tutor=tutor, species='dog', gender='M')
    
    service = Service.objects.create(
    name="Banho",
    price=30,
    duration_minutes=30,
    pet_shop=shop
)    
    appt = Appointment.objects.create(
        pet=pet,
        date='2026-01-01',
        time='10:00',
        service=None
    )

    set_current_pet_shop(shop)

    qs = Appointment.objects.all()

    assert qs.count() == 1
    assert qs.first().pet_shop_id == shop.id


@pytest.mark.django_db
def test_tenant_inativo_bloqueia():
    shop_inactive = PetShop.objects.create(
        name="Inativo",
        phone="333",
        is_active=False
    )

    set_current_pet_shop(shop_inactive)

    with pytest.raises(PermissionDenied):
        Appointment.objects.count()


@pytest.mark.django_db
def test_criacao_appointment_define_petshop():
    shop = PetShop.objects.create(name="Shop A", phone="111", is_active=True)
    set_current_pet_shop(shop)

    tutor = Tutor.objects.create(name="T2", phone="444", pet_shop=shop)
    pet = Pet.objects.create(name="Pet2", tutor=tutor, species='cat', gender='F')

    service = Service.objects.create(
    name="Banho",
    price=30,
    duration_minutes=30,
    pet_shop=shop
)

    appt = Appointment.objects.create(
        pet=pet,
        date='2026-01-02',
        time='11:00',
        service=None
    )

    assert appt.pet_shop_id == shop.id


@pytest.mark.django_db
def test_order_by_mantem_filtro_tenant():
    shop = PetShop.objects.create(name="Shop A", phone="111", is_active=True)
    set_current_pet_shop(shop)

    tutor = Tutor.objects.create(name="T3", phone="555", pet_shop=shop)
    pet = Pet.objects.create(name="Pet3", tutor=tutor, species='dog', gender='M')

    service = Service.objects.create(
    name="Banho",
    price=30,
    duration_minutes=30,
    pet_shop=shop
)

    Appointment.objects.create(
        pet=pet,
        date='2026-01-01',
        time='10:00',
        service=None
    )

    Appointment.objects.create(
        pet=pet,
        date='2026-01-02',
        time='11:00',
        service=None
    )

    qs = Appointment.objects.order_by('-date')

    assert all(a.pet_shop_id == shop.id for a in qs)


