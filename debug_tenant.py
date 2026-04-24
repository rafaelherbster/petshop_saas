import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.middleware import set_current_pet_shop, get_current_pet_shop
from django.core.exceptions import PermissionDenied
from agenda.models import Appointment
from core.models import PetShop

print("Debugging TenantQuerySet...")
print("Initial pet_shop in thread-local:", get_current_pet_shop())

# Test 1: Check what get_current_pet_shop returns after setting to None
set_current_pet_shop(None)
print("After set_current_pet_shop(None):", get_current_pet_shop())

# Test 2: Check the manager and queryset
print("\nAppointment.objects:", Appointment.objects)
print("Appointment.objects.__class__:", Appointment.objects.__class__)
print("Appointment.objects.get_queryset__:", Appointment.objects.get_queryset)
qs = Appointment.objects.get_queryset()
print("Queryset:", qs)
print("Queryset.__class__:", qs.__class__)

# Test 3: Check _apply_tenant_filter directly
print("\nTesting _apply_tenant_filter directly:")
try:
    result = qs._apply_tenant_filter()
    print("_apply_tenant_filter returned:", result)
except Exception as e:
    print("_apply_tenant_filter raised:", type(e).__name__, str(e))

# Test 4: Test all() method
print("\nTesting all() method:")
try:
    result = qs.all()
    print("all() returned:", result)
    print("all().__class__:", result.__class__)
except Exception as e:
    print("all() raised:", type(e).__name__, str(e))

# Test 5: Actually try to evaluate the queryset
print("\nTesting queryset evaluation:")
try:
    items = list(qs.all())
    print("list(all()) returned", len(items), "items")
    if items:
        print("First item pet_shop:", items[0].pet_shop)
except Exception as e:
    print("Evaluation raised:", type(e).__name__, str(e))