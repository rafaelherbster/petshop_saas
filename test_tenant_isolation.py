import pytest
from django.core.exceptions import PermissionDenied
from core.middleware import set_current_pet_shop
from agenda.models import Appointment
from cadastro.models import Tutor, Pet
from core.models import PetShop, UserProfile, User
from agenda.models import Service


@pytest.mark.django_db
def test_sem_tenant_gera_permission_denied():
    set_current_pet_shop(None)

    with pytest.raises(PermissionDenied):
        list(Appointment.objects.all())


@pytest.mark.django_db
def test_tenant_ativo_retorna_dados():
    shop = PetShop.objects.create(
        name="Petshop Teste",
        phone="11999999999",
        is_active=True
    )

    user = User.objects.create_user(
        username="testuser",
        email="test@test.com",
        password="test"
    )

    # O signal post_save já cria o UserProfile automaticamente
    # Então precisamos obtê-lo e atualizar
    profile = UserProfile.objects.get(user=user)
    profile.pet_shop = shop
    profile.role = 'owner'
    profile.save()

    set_current_pet_shop(shop)

    tutor1 = Tutor.objects.create(name="T1", phone="111", pet_shop=shop)
    tutor2 = Tutor.objects.create(name="T2", phone="222", pet_shop=shop)

    pet1 = Pet.objects.create(name="Pet1", tutor=tutor1, species='dog', gender='M')
    pet2 = Pet.objects.create(name="Pet2", tutor=tutor2, species='dog', gender='F')

    service = Service.objects.create(
        name="Banho",
        price=30,
        duration_minutes=30,
        pet_shop=shop
    )

    Appointment.objects.create(pet=pet1, date='2026-01-01', time='10:00', service=service)
    Appointment.objects.create(pet=pet2, date='2026-01-02', time='11:00', service=service)

    qs = Appointment.objects.all()

    assert qs.count() == 2
    assert all(a.pet_shop_id == shop.id for a in qs)


@pytest.mark.django_db
def test_tenant_inativo_bloqueia_ou_retorna_vazio():
    shop = PetShop.objects.create(name="Ativo", phone="111", is_active=True)
    shop_inactive = PetShop.objects.create(name="Inativo", phone="222", is_active=False)

    set_current_pet_shop(shop)

    tutor = Tutor.objects.create(name="T1", phone="111", pet_shop=shop)
    pet = Pet.objects.create(name="Pet1", tutor=tutor, species='dog', gender='M')

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
        service=service
    )

    set_current_pet_shop(shop_inactive)

    try:
        qs = Appointment.objects.all()
        # comportamento aceitável: retornar vazio
        assert qs.count() == 0
    except PermissionDenied:
        # comportamento aceitável: bloquear
        assert True


@pytest.mark.django_db
def test_criacao_automatica_define_petshop():
    shop = PetShop.objects.create(name="Shop", phone="333", is_active=True)
    set_current_pet_shop(shop)

    tutor = Tutor.objects.create(name="T3", phone="333", pet_shop=shop)
    pet = Pet.objects.create(name="Pet3", tutor=tutor, species='cat', gender='M')

    service = Service.objects.create(
        name="Banho",
        price=30,
        duration_minutes=30,
        pet_shop=shop
    )

    appt = Appointment.objects.create(
        pet=pet,
        date='2026-01-03',
        time='14:00',
        service=service
    )

    assert appt.pet_shop_id == shop.id