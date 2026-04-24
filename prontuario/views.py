from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from cadastro.models import Pet
from prontuario.models import HealthRecord
from core.decorators import tenant_required


@tenant_required
@login_required
def health_record_create(request, slug):
    pet_shop = request.pet_shop
    pet_id = request.GET.get('pet') or request.POST.get('pet')

    if request.method == 'POST':
        pet = get_object_or_404(Pet, pk=request.POST.get('pet'), pet_shop=pet_shop)

        record = HealthRecord.objects.create(
            pet=pet,
            pet_shop=pet_shop,  # 🔴 IMPORTANTE (se existir no model)
            date=request.POST.get('date'),
            type=request.POST.get('type'),
            description=request.POST.get('description'),
            next_due=request.POST.get('next_due') or None,
        )

        return redirect('pet_detail', slug=slug, pk=pet.pk)

    pets = Pet.objects.filter(pet_shop=pet_shop).select_related('tutor').order_by('name')

    return render(request, 'prontuario/health_record_form.html', {
        'pets': pets,
        'selected_pet': pet_id,
    })


@tenant_required
@login_required
def health_record_edit(request, slug, pk):
    pet_shop = request.pet_shop

    record = get_object_or_404(
        HealthRecord,
        pk=pk,
        pet__pet_shop=pet_shop  # 🔐 isolamento via relacionamento
    )

    if request.method == 'POST':
        record.date = request.POST.get('date')
        record.type = request.POST.get('type')
        record.description = request.POST.get('description')
        record.next_due = request.POST.get('next_due') or None
        record.save()

        return redirect('pet_detail', slug=slug, pk=record.pet.pk)

    return render(request, 'prontuario/health_record_form.html', {
        'record': record,
        'pets': [record.pet],
    })


@tenant_required
@login_required
def health_record_delete(request, slug, pk):
    pet_shop = request.pet_shop

    record = get_object_or_404(
        HealthRecord,
        pk=pk,
        pet__pet_shop=pet_shop
    )

    if request.method == 'POST':
        pet_pk = record.pet.pk
        record.delete()
        return redirect('pet_detail', slug=slug, pk=pet_pk)

    return render(request, 'prontuario/health_record_confirm_delete.html', {
        'record': record
    })