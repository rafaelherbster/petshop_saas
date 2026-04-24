# -*- coding: utf-8 -*-
from datetime import date, datetime
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from agenda.models import Service, Appointment
from cadastro.models import Tutor, Pet
from core.models import PetShop, BusinessHours
from publico.models import ClientToken



def schedule_view(request, shop_slug):
    pet_shop = get_object_or_404(PetShop, slug=shop_slug)
    services = Service.objects.filter(pet_shop=pet_shop, is_active=True)

    if request.method == 'POST':
        owner_name = request.POST.get('owner_name')
        phone = request.POST.get('phone')

        tutor, _ = Tutor.objects.get_or_create(
            pet_shop=pet_shop,
            phone=phone,
            defaults={'name': owner_name},
        )

        if not tutor.name:
            tutor.name = owner_name
            tutor.save(update_fields=['name'])

        pet_name = request.POST.get('pet_name')
        species = request.POST.get('species', 'dog')
        breed = request.POST.get('breed', '')
        notes = request.POST.get('notes', '')

        pet, _ = Pet.objects.get_or_create(
            tutor=tutor,
            name=pet_name,
            defaults={
                'pet_shop': pet_shop,
                'species': species,
                'breed': breed,
                'gender': 'M',
                'notes': notes,
            },
        )

        service = Service.objects.get(
            pk=request.POST.get('service'),
            pet_shop=pet_shop
        )

        # ✅ Conversão de data e hora
        try:
            apt_date = datetime.strptime(
                request.POST.get('date'), "%Y-%m-%d"
            ).date()

            apt_time = datetime.strptime(
                request.POST.get('time'), "%H:%M"
            ).time()
        except Exception:
            messages.error(request, 'Data ou horário inválido.')
            return render(request, 'publico/schedule.html', {
                'pet_shop': pet_shop,
                'services': services,
                'default_date': date.today(),
            })

        # =========================
        # 🔥 VALIDAÇÃO DE HORÁRIO
        # =========================

        weekday = apt_date.weekday()  # 0 = segunda

        business_hours = BusinessHours.objects.filter(
            pet_shop=pet_shop,
            weekday=weekday
        ).first()

        # 🚫 Dia fechado
        if not business_hours:
            messages.error(request, 'Petshop não funciona neste dia.')
            return render(request, 'publico/schedule.html', {
                'pet_shop': pet_shop,
                'services': services,
                'default_date': date.today(),
            })

        # 🚫 Fora do horário
        if not (business_hours.opening_time <= apt_time <= business_hours.closing_time):
            messages.error(request, 'Fora do horário de funcionamento.')
            return render(request, 'publico/schedule.html', {
                'pet_shop': pet_shop,
                'services': services,
                'default_date': date.today(),
            })

        # =========================
        # ✅ CRIAÇÃO DO AGENDAMENTO
        # =========================

        try:
            appointment = Appointment.objects.create(
                pet=pet,
                service=service,
                date=apt_date,
                time=apt_time,
                status='agendado',
            )

            client_token = ClientToken.objects.create(
                pet_shop=pet_shop,
                phone=phone,
                pet_name=pet_name,
            )

            return redirect('public_success', token=client_token.token)

        except IntegrityError:
            messages.error(
                request,
                'Horário indisponível. Por favor, escolha outro.'
            )

    context = {
        'pet_shop': pet_shop,
        'services': services,
        'default_date': date.today(),
    }

    return render(request, 'publico/schedule.html', context)

def success_view(request, token):
    client_token = get_object_or_404(ClientToken, token=token)
    pet_shop = client_token.pet_shop

    tutor = Tutor.objects.filter(pet_shop=pet_shop, phone=client_token.phone).first()
    appointments = []
    payment = None
    pix_qr_manual = None
    pix_amount = None
    has_pix_key = bool(pet_shop.pix_key)
    show_pix = False

    if tutor:
        appointments = Appointment.objects.filter(
            pet__tutor=tutor,
            pet_shop=pet_shop,
        ).select_related('service', 'pet').order_by('-date', '-time')[:5]

        if appointments:
            apt = appointments[0]
            pix_amount = apt.service.price if apt.service else None

            # Cria Payment para registrar o pagamento
            financeiro = __import__('financeiro.models', fromlist=['Payment'])
            Payment = financeiro.Payment
            payment, _ = Payment.objects.get_or_create(
                appointment=apt,
                defaults={
                    'amount': pix_amount,
                    'method': 'pix',
                    'status': 'pending',
                }
            )

            # QR code manual (upload do dono)
            if pet_shop.pix_qr_code:
                pix_qr_manual = pet_shop.pix_qr_code.url
                show_pix = has_pix_key

    context = {
        'client_token': client_token,
        'appointments': appointments,
        'pix_qr_manual': pix_qr_manual,
        'pix_amount': pix_amount,
        'payment': payment,
        'has_pix_key': has_pix_key,
        'show_pix': show_pix,
    }
    return render(request, 'publico/success.html', context)
