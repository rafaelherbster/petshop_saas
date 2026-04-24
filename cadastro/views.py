from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from cadastro.models import Pet, Tutor, LoyaltyCard
from core.decorators import tenant_required

@login_required
@tenant_required
def tutor_list(request, slug):
    query = request.GET.get('q', '')
    tutors = Tutor.objects.filter(pet_shop=request.pet_shop)

    if query:
        tutors = tutors.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'tutors': tutors,
        'query': query,
    }

    if request.htmx:
        return render(request, 'cadastro/partials/tutor_list.html', context)
    return render(request, 'cadastro/tutor_list.html', context)

@login_required
@tenant_required
def tutor_create(request, slug):
    if request.method == 'POST':
        tutor = Tutor.objects.create(
            
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email', ''),
            cpf=request.POST.get('cpf', ''),
            address=request.POST.get('address', ''),
            notes=request.POST.get('notes', ''),
            pet_shop=request.pet_shop
        )

        if request.htmx:
            return render(request, 'cadastro/partials/tutor_row.html', {'tutor': tutor})

        return redirect('tutor_detail', slug=slug, pk=tutor.pk)

    return render(request, 'cadastro/tutor_form.html')


@login_required
@tenant_required
def tutor_detail(request, slug, pk):
    tutor = get_object_or_404(Tutor, pk=pk, pet_shop=request.pet_shop)
    pets = tutor.pets.all()

    return render(request, 'cadastro/tutor_detail.html', {
        'tutor': tutor,
        'pets': pets
    })


@login_required
@tenant_required
def tutor_edit(request, slug, pk):
    tutor = get_object_or_404(Tutor, pk=pk, pet_shop=request.pet_shop)

    if request.method == 'POST':
        tutor.name = request.POST.get('name')
        tutor.phone = request.POST.get('phone')
        tutor.email = request.POST.get('email', '')
        tutor.cpf = request.POST.get('cpf', '')
        tutor.address = request.POST.get('address', '')
        tutor.notes = request.POST.get('notes', '')
        tutor.save()

        return redirect('tutor_detail', slug=slug, pk=tutor.pk)

    return render(request, 'cadastro/tutor_edit.html', {'tutor': tutor})


@login_required
@tenant_required
def tutor_delete(request, slug, pk):
    tutor = get_object_or_404(Tutor, pk=pk, pet_shop=request.pet_shop)

    if request.method == 'POST':
        tutor.delete()
        return redirect('tutor_list', slug=slug)

    return render(request, 'cadastro/tutor_confirm_delete.html', {'tutor': tutor})


@login_required
@tenant_required
def pet_list(request, slug):
    query = request.GET.get('q', '')

    # ✅ agora filtrando por tenant
    pets = Pet.objects.select_related('tutor').filter(pet_shop=request.pet_shop)

    if query:
        pets = pets.filter(
            Q(name__icontains=query) |
            Q(tutor__name__icontains=query)
        )

    if request.htmx:
        return render(request, 'cadastro/partials/pet_list.html', {'pets': pets})

    return render(request, 'cadastro/pet_list.html', {
        'pets': pets,
        'query': query
    })


@login_required
@tenant_required
def pet_create(request, slug):
    if request.method == 'POST':
        tutor = get_object_or_404(
            Tutor,
            pk=request.POST.get('tutor'),
            pet_shop=request.pet_shop
        )

        pet = Pet.objects.create(
            tutor=tutor,
            pet_shop=request.pet_shop,  
            name=request.POST.get('name'),
            species=request.POST.get('species'),
            breed=request.POST.get('breed', ''),
            size=request.POST.get('size', ''),
            gender=request.POST.get('gender'),
            birth_date=request.POST.get('birth_date') or None,
            color=request.POST.get('color', ''),
            notes=request.POST.get('notes', ''),
            photo=request.FILES.get('photo'),
        )

        return redirect('pet_detail', slug=slug, pk=pet.pk)

    tutors = Tutor.objects.filter(pet_shop=request.pet_shop).order_by('name')

    return render(request, 'cadastro/pet_form.html', {'tutors': tutors})


@login_required
@tenant_required
def pet_detail(request, slug, pk):
    # ✅ CORREÇÃO PRINCIPAL
    pet = get_object_or_404(Pet, pk=pk, pet_shop=request.pet_shop)

    health_records = pet.health_records.order_by('-date')[:10]
    appointments = pet.appointments.order_by('-date')[:10]

    return render(request, 'cadastro/pet_detail.html', {
        'pet': pet,
        'health_records': health_records,
        'appointments': appointments,
    })


@login_required
@tenant_required
def pet_edit(request, slug, pk):
    # ✅ corrigido
    pet = get_object_or_404(Pet, pk=pk, pet_shop=request.pet_shop)

    if request.method == 'POST':
        pet.name = request.POST.get('name')
        pet.species = request.POST.get('species')
        pet.breed = request.POST.get('breed', '')
        pet.size = request.POST.get('size', '')
        pet.gender = request.POST.get('gender')
        pet.birth_date = request.POST.get('birth_date') or None
        pet.color = request.POST.get('color', '')
        pet.notes = request.POST.get('notes', '')

        if request.FILES.get('photo'):
            pet.photo = request.FILES['photo']

        pet.save()
        return redirect('pet_detail', slug=slug, pk=pet.pk)

    tutors = Tutor.objects.filter(pet_shop=request.pet_shop).order_by('name')

    return render(request, 'cadastro/pet_edit.html', {
        'pet': pet,
        'tutors': tutors
    })


@login_required
@tenant_required
def pet_delete(request, slug, pk):
    # ✅ corrigido
    pet = get_object_or_404(Pet, pk=pk, pet_shop=request.pet_shop)

    if request.method == 'POST':
        pet.delete()
        return redirect('pet_list', slug=slug)

    return render(request, 'cadastro/pet_confirm_delete.html', {'pet': pet})


@login_required
@tenant_required
def loyalty_activate(request, slug, pk):
    pet = get_object_or_404(Pet, pk=pk, pet_shop=request.pet_shop)

    card, created = LoyaltyCard.objects.get_or_create(
        pet=pet,
        defaults={'max_visits': 10},
    )

    if created:
        messages.success(request, 'Cartão fidelidade ativado!')
    elif card.redeemed_at:
        card.redeemed_at = None
        card.visits_count = pet.visit_count
        card.save()
        messages.success(request, 'Cartão fidelidade reativado!')

    return redirect('pet_detail', slug=slug, pk=pet.pk)


@login_required
@tenant_required
def loyalty_redeem(request, slug, pk):
    card = get_object_or_404(
        LoyaltyCard,
        pk=pk,
        pet__pet_shop=request.pet_shop
    )

    if card.is_complete:
        from django.utils import timezone
        card.redeemed_at = timezone.now()
        card.visits_count = 0
        card.save()

        messages.success(
            request,
            f'Cartão resgatado! Próximo ciclo: 0/{card.max_visits}'
        )

    return redirect('pet_detail', slug=slug, pk=card.pet.pk)