from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from agenda.models import Appointment, Service
from core.decorators import tenant_required


@tenant_required
@login_required
def appointment_list(request, slug):
    today = date.today()

    date_param = request.GET.get('date')
    try:
        target_date = date.fromisoformat(date_param) if date_param else today
    except ValueError:
        target_date = today

    appointments = Appointment.objects.filter(
        pet_shop=request.pet_shop,
        date=target_date,
    ).select_related('pet', 'service').order_by('time')

    context = {
        'pet_shop': request.pet_shop,
        'appointments': appointments,
        'date': target_date,
        'prev_date': target_date - timedelta(days=1),
        'next_date': target_date + timedelta(days=1),
    }

    if request.htmx:
        return render(request, 'agenda/partials/appointment_list.html', context)

    return render(request, 'agenda/appointment_list.html', context)


@tenant_required
@login_required
def appointment_create(request, slug):
    from cadastro.models import Pet

    if request.method == 'POST':
        pet = get_object_or_404(
            Pet,
            pk=request.POST.get('pet'),
            pet_shop=request.pet_shop
        )

        service = get_object_or_404(
            Service,
            pk=request.POST.get('service'),
            pet_shop=request.pet_shop
        )

        Appointment.objects.create(
            pet_shop=request.pet_shop,
            pet=pet,
            service=service,
            date=request.POST.get('date'),
            time=request.POST.get('time'),
            notes=request.POST.get('notes', ''),
        )

        return redirect('appointment_list', slug=slug)

    pets = Pet.objects.filter(
        pet_shop=request.pet_shop
    ).select_related('tutor').order_by('name')

    services = Service.objects.filter(
        pet_shop=request.pet_shop,
        is_active=True
    )

    return render(request, 'agenda/appointment_form.html', {
        'pet_shop': request.pet_shop,
        'pets': pets,
        'services': services,
        'default_date': date.today(),
    })


@tenant_required
@login_required
def appointment_detail(request, slug, pk):
    appointment = get_object_or_404(
        Appointment,
        pk=pk,
        pet_shop=request.pet_shop
    )

    return render(request, 'agenda/appointment_detail.html', {
        'pet_shop': request.pet_shop,
        'appointment': appointment
    })


@tenant_required
@login_required
def appointment_edit(request, slug, pk):
    from cadastro.models import Pet

    appointment = get_object_or_404(
        Appointment,
        pk=pk,
        pet_shop=request.pet_shop
    )

    if request.method == 'POST':
        pet = get_object_or_404(
            Pet,
            pk=request.POST.get('pet'),
            pet_shop=request.pet_shop
        )

        service = get_object_or_404(
            Service,
            pk=request.POST.get('service'),
            pet_shop=request.pet_shop
        )

        appointment.pet = pet
        appointment.service = service
        appointment.date = request.POST.get('date')
        appointment.time = request.POST.get('time')
        appointment.status = request.POST.get('status', appointment.status)
        appointment.notes = request.POST.get('notes', '')
        appointment.save()

        return redirect('appointment_list', slug=slug)

    pets = Pet.objects.filter(
        pet_shop=request.pet_shop
    ).select_related('tutor').order_by('name')

    services = Service.objects.filter(
        pet_shop=request.pet_shop,
        is_active=True
    )

    return render(request, 'agenda/appointment_edit.html', {
        'pet_shop': request.pet_shop,
        'appointment': appointment,
        'pets': pets,
        'services': services,
    })


@tenant_required
@login_required
def appointment_delete(request, slug, pk):
    appointment = get_object_or_404(
        Appointment,
        pk=pk,
        pet_shop=request.pet_shop
    )

    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list', slug=slug)

    return render(request, 'agenda/appointment_confirm_delete.html', {
        'pet_shop': request.pet_shop,
        'appointment': appointment
    })


@tenant_required
@login_required
def appointment_quick_status(request, slug, pk):
    appointment = get_object_or_404(
        Appointment,
        pk=pk,
        pet_shop=request.pet_shop
    )

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid = [s[0] for s in Appointment.STATUS_CHOICES]

        if new_status in valid:
            appointment.status = new_status
            appointment.save()
            messages.success(
                request,
                f'Status alterado para "{appointment.get_status_display()}".'
            )

    return redirect('appointment_detail', slug=slug, pk=pk)


@tenant_required
@login_required
def payment_quick_status(request, slug, pk):
    from financeiro.models import Payment

    payment = get_object_or_404(
        Payment,
        pk=pk,
        appointment__pet_shop=request.pet_shop
    )

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid = [s[0] for s in Payment.STATUS_CHOICES]

        if new_status in valid:
            old_status = payment.status
            payment.status = new_status
            payment.save()

            if new_status == 'paid' and old_status != 'paid':
                appointment = payment.appointment

                if appointment.status == 'agendado':
                    appointment.status = 'confirmado'
                    appointment.save()
                    messages.success(
                        request,
                        f'Pagamento confirmado e agendamento atualizado para "{appointment.get_status_display()}".'
                    )
                else:
                    messages.success(
                        request,
                        f'Status do pagamento alterado para "{payment.get_status_display()}".'
                    )
            else:
                messages.success(
                    request,
                    f'Status do pagamento alterado para "{payment.get_status_display()}".'
                )

    return redirect('appointment_detail', slug=slug, pk=payment.appointment.pk)


@tenant_required
@login_required
def service_list(request, slug):
    services = Service.objects.filter(
        pet_shop=request.pet_shop
    )

    return render(request, 'agenda/service_list.html', {
        'pet_shop': request.pet_shop,
        'services': services
    })


@tenant_required
@login_required
def service_create(request, slug):
    if request.method == 'POST':
        Service.objects.create(
            pet_shop=request.pet_shop,
            name=request.POST.get('name'),
            price=request.POST.get('price') or 0,
            duration_minutes=request.POST.get('duration_minutes') or 60,
            description=request.POST.get('description', ''),
        )
        return redirect('service_list', slug=slug)

    return render(request, 'agenda/service_form.html', {
        'pet_shop': request.pet_shop
    })


@tenant_required
@login_required
def service_edit(request, slug, pk):
    service = get_object_or_404(
        Service,
        pk=pk,
        pet_shop=request.pet_shop
    )

    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.price = request.POST.get('price') or 0
        service.duration_minutes = request.POST.get('duration_minutes') or 60
        service.description = request.POST.get('description', '')
        service.is_active = request.POST.get('is_active') == 'on'
        service.save()

        return redirect('service_list', slug=slug)

    return render(request, 'agenda/service_edit.html', {
        'pet_shop': request.pet_shop,
        'service': service
    })


@tenant_required
@login_required
def service_delete(request, slug, pk):
    service = get_object_or_404(
        Service,
        pk=pk,
        pet_shop=request.pet_shop
    )

    if request.method == 'POST':
        service.delete()
        return redirect('service_list', slug=slug)

    return render(request, 'agenda/service_confirm_delete.html', {
        'pet_shop': request.pet_shop,
        'service': service
    })