# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError

from core.models import PetShop, TenantModel


class Service(TenantModel):
    pet_shop = models.ForeignKey(PetShop, on_delete=models.CASCADE, related_name='services')
    name = models.CharField('Nome', max_length=100)
    price = models.DecimalField('Preço Base', max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField('Duração (min)', default=60)
    description = models.TextField('Descrição', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - R$ {self.price}'


class Appointment(TenantModel):
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('confirmado', 'Confirmado'),
        ('atendido', 'Atendido'),
        ('cancelado', 'Cancelado'),
        ('no_show', 'Não Compareceu'),
    ]

    # NÃO definir pet_shop aqui - já vem do TenantModel!
    pet = models.ForeignKey('cadastro.Pet', on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='appointments')
    date = models.DateField('Data')
    time = models.TimeField('Horário')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='agendado')
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.pet and self.pet.pet_shop_id != self.pet_shop_id:
            raise ValidationError("Pet pertence a outro tenant")

        if self.service and self.service.pet_shop_id != self.pet_shop_id:
            raise ValidationError("Service pertence a outro tenant")

    class Meta:
        ordering = ['date', 'time']
        indexes = [
        models.Index(fields=['pet_shop']),
        ]

    def __str__(self):
        return f'{self.pet.name} - {self.service} - {self.date} {self.time}'

    @property
    def status_color(self):
        colors = {
            'agendado': 'bg-yellow-100 text-yellow-800',
            'confirmado': 'bg-blue-100 text-blue-800',
            'atendido': 'bg-green-100 text-green-800',
            'cancelado': 'bg-red-100 text-red-800',
            'no_show': 'bg-gray-100 text-gray-800',
        }
        return colors.get(self.status, 'bg-gray-100 text-gray-800')
