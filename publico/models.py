# -*- coding: utf-8 -*-
import secrets
from django.db import models

from core.models import TenantModel


class ClientToken(TenantModel):
    """Token generated per public booking, so the client can track status without an account."""
    pet_shop = models.ForeignKey('core.PetShop', on_delete=models.CASCADE, related_name='client_tokens')
    token = models.CharField('Token', max_length=12, unique=True)
    phone = models.CharField('Telefone', max_length=20)
    pet_name = models.CharField('Nome do Pet', max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Token de Acesso'
        indexes = [
        models.Index(fields=['pet_shop']),
        ]

    def __str__(self):
        return self.token

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(6)
        super().save(*args, **kwargs)
