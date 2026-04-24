# -*- coding: utf-8 -*-
from django.db import models

from core.models import PetShop, TenantModel


class Tutor(TenantModel):
    name = models.CharField('Nome', max_length=200)
    phone = models.CharField('Telefone', max_length=20)
    email = models.EmailField(blank=True, null=True)
    cpf = models.CharField('CPF', max_length=14, blank=True, null=True)
    address = models.CharField('Endereço', max_length=300, blank=True)
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tutor'
        constraints = [
            models.UniqueConstraint(
                fields=['pet_shop', 'email'],
                name='unique_tutor_email_per_petshop'
            )
        ]
        indexes = [
        models.Index(fields=['pet_shop']),
        ]

    def __str__(self):
        return self.name



class Pet(TenantModel):
    SPECIES_CHOICES = [
        ('dog', 'Cachorro'),
        ('cat', 'Gato'),
        ('bird', 'Pássaro'),
        ('rabbit', 'Coelho'),
        ('hamster', 'Hamster'),
        ('fish', 'Peixe'),
        ('reptile', 'Réptil'),
        ('other', 'Outro'),
    ]
    SIZE_CHOICES = [
        ('small', 'Pequeno'),
        ('medium', 'Médio'),
        ('large', 'Grande'),
        ('giant', 'Gigante'),
    ]
    GENDER_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField('Nome', max_length=100)
    species = models.CharField('Espécie', max_length=20, choices=SPECIES_CHOICES, default='dog')
    breed = models.CharField('Raça', max_length=100, blank=True)
    size = models.CharField('Porte', max_length=20, choices=SIZE_CHOICES, blank=True)
    gender = models.CharField('Sexo', max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField('Data de Nascimento', blank=True, null=True)
    color = models.CharField('Cor', max_length=50, blank=True)
    notes = models.TextField('Observações', blank=True)
    visit_count = models.PositiveIntegerField(default=0)
    photo = models.ImageField('Foto', upload_to='pets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_species_display()})'


class LoyaltyCard(TenantModel):
    pet = models.OneToOneField(Pet, on_delete=models.CASCADE, related_name='loyalty_card')
    max_visits = models.PositiveIntegerField('Visitas para desconto', default=10)
    visits_count = models.PositiveIntegerField('Visitas', default=0)
    redeemed_at = models.DateTimeField('Resgatado em', blank=True, null=True)

    class Meta:
        verbose_name = 'Cartão Fidelidade'

    def __str__(self):
        return f'{self.pet.name} — {self.visits_count}/{self.max_visits}'

    @property
    def is_complete(self):
        return self.visits_count >= self.max_visits and not self.redeemed_at
