# -*- coding: utf-8 -*-
from django.db import models

from core.models import PetShop, TenantModel


class HealthRecord(TenantModel):
    TYPE_CHOICES = [
        ('vacina', 'Vacina'),
        ('vermifugo', 'Vermífugo'),
        ('alergia', 'Alergia'),
        ('doenca', 'Doença'),
        ('cirurgia', 'Cirurgia'),
        ('medicamento', 'Medicamento'),
        ('outro', 'Outro'),
    ]

    pet = models.ForeignKey('cadastro.Pet', on_delete=models.CASCADE, related_name='health_records')
    pet_shop = models.ForeignKey(PetShop, on_delete=models.CASCADE, related_name='health_records')
    date = models.DateField('Data')
    type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES)
    description = models.TextField('Descrição')
    next_due = models.DateField('Próximo Vencimento', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        indexes = [
        models.Index(fields=['pet_shop']),
        ]

    def __str__(self):
        return f'{self.pet.name} - {self.get_type_display()} - {self.date}'
