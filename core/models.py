# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied
from django.db import models
from core.middleware import get_current_pet_shop


class TenantQuerySet(models.QuerySet):

    def _get_tenant(self):
        pet_shop = get_current_pet_shop()

        if pet_shop is None:
            raise PermissionDenied("Tenant não definido")

        if not pet_shop.is_active:
            raise PermissionDenied("Tenant inativo")

        return pet_shop

    def _apply_tenant_filter(self):
        return super().filter(pet_shop=self._get_tenant())

    def all(self):
        return self._apply_tenant_filter()

    def filter(self, *args, **kwargs):
        if 'pet_shop' in kwargs:
            return super().filter(*args, **kwargs)
        return super().filter(*args, **kwargs).filter(
            pet_shop=self._get_tenant()
        )

    def exclude(self, *args, **kwargs):
        return super().exclude(*args, **kwargs).filter(
            pet_shop=self._get_tenant()
        )

    def get(self, *args, **kwargs):
        if 'pet_shop' in kwargs:
            return super().get(*args, **kwargs)
        return super().get(pet_shop=self._get_tenant(), *args, **kwargs)

    # 🔥 ESSENCIAL — CORRIGE SEU BUG
    def count(self):
        qs = self._apply_tenant_filter()
        return super(TenantQuerySet, qs).count()

    def exists(self):
        qs = self._apply_tenant_filter()
        return super(TenantQuerySet, qs).exists()

    def first(self):
        self._get_tenant()
        return super().first()

    def last(self):
        self._get_tenant()
        return super().last()
    
    def delete(self):
        self._get_tenant()
        return super().delete()
    
    def update(self, **kwargs):
        self._get_tenant()

        if 'pet_shop' in kwargs:
            raise PermissionDenied("Não é permitido alterar o tenant")

        return super().update(**kwargs)
    
    def raw(self, *args, **kwargs):
        raise PermissionDenied("raw() não permitido em ambiente multi-tenant")


    def extra(self, *args, **kwargs):
        raise PermissionDenied("extra() não permitido em ambiente multi-tenant")

class TenantManager(models.Manager):
    
    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().all()

    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.get_queryset().get(*args, **kwargs)

    def create(self, **kwargs):
        if 'pet_shop' not in kwargs:
            pet_shop = get_current_pet_shop()
            if pet_shop is None:
                raise PermissionDenied("Não é possível criar registros sem tenant definido")
            if not pet_shop.is_active:
                raise PermissionDenied("Tenant inativo não pode criar registros")
            kwargs['pet_shop'] = pet_shop

        return super().create(**kwargs)
    
class TenantModel(models.Model):
    pet_shop = models.ForeignKey(
        'core.PetShop',
        on_delete=models.CASCADE
    )

    objects = TenantManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pet_shop_id:
            pet_shop = get_current_pet_shop()
            if pet_shop is None:
                raise PermissionDenied("Tenant não definido")
            if not pet_shop.is_active:
                raise PermissionDenied("Tenant inativo")
            self.pet_shop = pet_shop

        super().save(*args, **kwargs)
    


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class PetShop(models.Model):
    name = models.CharField('Nome Fantasia', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    cnpj = models.CharField('CNPJ', max_length=18, blank=True, null=True)
    phone = models.CharField('Telefone', max_length=20)
    address = models.CharField('Endereço', max_length=300, blank=True)
    pix_key = models.CharField('Chave PIX', max_length=200, blank=True, null=True, help_text='Email, CPF, CNPJ ou telefone')
    pix_qr_code = models.ImageField('QR Code PIX', upload_to='pix_qrcodes/', blank=True, null=True, help_text='Faça upload do QR code PIX gerado pelo seu app bancário')
    is_active = models.BooleanField('Ativo', default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pet Shop'
        

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            base = slugify(self.name) or str(self.pk)
            slug = base
            counter = 1
            while PetShop.objects.filter(slug=slug).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Proprietário'),
        ('employee', 'Funcionário'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    pet_shop = models.ForeignKey(PetShop, on_delete=models.CASCADE, related_name='users', null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='owner')

    def __str__(self):
        return f'{self.user.email} - {self.role}'

class BusinessHours(TenantModel):
    WEEKDAYS = [
        (0, 'Segunda'),
        (1, 'Terça'),
        (2, 'Quarta'),
        (3, 'Quinta'),
        (4, 'Sexta'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    pet_shop = models.ForeignKey('core.PetShop', on_delete=models.CASCADE, related_name='business_hours')
    weekday = models.IntegerField(choices=WEEKDAYS)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        unique_together = ('pet_shop', 'weekday')
        ordering = ['weekday']
        indexes = [
        models.Index(fields=['pet_shop']),
        ]

    def __str__(self):
        return f"{self.get_weekday_display()} - {self.opening_time} às {self.closing_time}"
    
# ============================================================
# PLANOS E ASSINATURAS
# ============================================================

class Plan(models.Model):
    """Planos de assinatura"""

    class Tier(models.TextChoices):
        FREE = 'free', 'Gratuito'
        STARTER = 'starter', 'Iniciante'
        PRO = 'pro', 'Profissional'
        ENTERPRISE = 'enterprise', 'Enterprise'

    tier = models.CharField(max_length=20, choices=Tier.choices, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    monthly_price = models.IntegerField(default=0)  # Em centavos
    yearly_price = models.IntegerField(default=0)
    max_pets = models.IntegerField(default=10)
    max_services = models.IntegerField(default=5)
    max_employees = models.IntegerField(default=1)
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    @classmethod
    def get_default(cls):
        return cls.objects.filter(is_default=True).first()


class Subscription(models.Model):
    """Assinatura de um pet shop"""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Ativa'
        CANCELED = 'canceled', 'Cancelada'
        EXPIRED = 'expired', 'Expirada'

    pet_shop = models.OneToOneField(PetShop, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.pet_shop.name} - {self.plan.name}"

    @property
    def is_active(self):
        from django.utils import timezone
        return self.status == self.Status.ACTIVE and (not self.expires_at or self.expires_at > timezone.now())
replace_all: False

