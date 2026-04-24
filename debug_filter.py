import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.middleware import set_current_pet_shop, get_current_pet_shop
from django.core.exceptions import PermissionDenied
from agenda.models import Appointment
from core.models import PetShop

print("=== Debugging filter method ===")

# Create a test shop
shop = PetShop.objects.create(name="Debug Shop", phone="111", is_active=True)
print(f"Created shop: {shop.id}")

# Set the tenant
set_current_pet_shop(shop)
print(f"Current pet_shop: {get_current_pet_shop()}")

# Get the queryset
qs = Appointment.objects.all()
print(f"Initial queryset: {qs}")
print(f"Initial queryset type: {type(qs)}")

# Try to apply filter manually
print("\n--- Testing _apply_tenant_filter ---")
try:
    filtered_qs = qs._apply_tenant_filter()
    print(f"_apply_tenant_filter result: {filtered_qs}")
    print(f"_apply_tenant_filter type: {type(filtered_qs)}")
except Exception as e:
    print(f"_apply_tenant_filter error: {type(e).__name__}: {e}")

# Try the filter method without arguments
print("\n--- Testing filter() ---")
try:
    result = qs.filter()
    print(f"filter() result: {result}")
    print(f"filter() type: {type(result)}")
except Exception as e:
    print(f"filter() error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Try the filter method with arguments
print("\n--- Testing filter(pet_shop=shop) ---")
try:
    result = qs.filter(pet_shop=shop)
    print(f"filter(pet_shop=shop) result: {result}")
    print(f"filter(pet_shop=shop) type: {type(result)}")
except Exception as e:
    print(f"filter(pet_shop=shop) error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()