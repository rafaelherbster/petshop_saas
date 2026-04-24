from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from agenda.models import Appointment
from cadastro.models import LoyaltyCard
from core.decorators import tenant_required
from financeiro.models import Payment

@tenant_required
@login_required
def register_payment(request, slug, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        pk=appointment_id,
        pet_shop=request.pet_shop
    )

    if request.method == 'POST':
        amount = request.POST.get('amount') or appointment.service.price
        method = request.POST.get('method', 'pix')

        payment, created = Payment.objects.get_or_create(
            appointment=appointment,
            defaults={'amount': amount, 'method': method, 'status': 'paid'},
        )

        if not created:
            payment.amount = amount
            payment.method = method
            payment.save()

        return redirect('appointment_detail', slug=slug, pk=appointment.pk)

    return render(request, 'financeiro/payment_form.html', {
        'appointment': appointment
    })


@login_required
@tenant_required
def edit_payment(request, slug, pk):
    payment = get_object_or_404(
        Payment,
        pk=pk,
        appointment__pet_shop=request.pet_shop
    )

    if request.method == 'POST':
        payment.amount = request.POST.get('amount') or payment.amount
        payment.method = request.POST.get('method', payment.method)
        payment.status = request.POST.get('status', payment.status)
        payment.save()

        return redirect(
            'appointment_detail',
            slug=slug,
            pk=payment.appointment.pk
        )

    return render(request, 'financeiro/payment_edit.html', {
        'pet_shop': request.pet_shop,
        'payment': payment,
        'appointment': payment.appointment,
    })


@login_required
@tenant_required
def payment_quick_status(request, slug, pk):
    payment = get_object_or_404(
        Payment,
        pk=pk,
        appointment__pet_shop=request.pet_shop
    )

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid = [s[0] for s in Payment.STATUS_CHOICES]

        if new_status in valid:
            payment.status = new_status
            payment.save()

            from django.contrib import messages
            messages.success(
                request,
                f'Status alterado para "{payment.get_status_display()}".'
            )

    return redirect(
        'appointment_detail',
        slug=slug,
        pk=payment.appointment.pk
    )