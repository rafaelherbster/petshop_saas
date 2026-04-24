# -*- coding: utf-8 -*-
from django.db import models

from core.models import TenantModel


class Payment(TenantModel):
    METHOD_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao_credito', 'Cartão Crédito'),
        ('cartao_debito', 'Cartão Débito'),
    ]
    STATUS_CHOICES = [
        ('paid', 'Pago'),
        ('pending', 'Pendente'),
        ('refunded', 'Reembolsado'),
    ]

    appointment = models.OneToOneField('agenda.Appointment', on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    method = models.CharField('Método', max_length=20, choices=METHOD_CHOICES)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
        models.Index(fields=['pet_shop']),
        ]

    def __str__(self):
        return f'R$ {self.amount} - {self.get_method_display()}'
