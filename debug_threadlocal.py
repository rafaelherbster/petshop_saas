import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.middleware import set_current_pet_shop, get_current_pet_shop
from core.models import PetShop

print("Testing thread-local functions...")
print("Initial state:", get_current_pet_shop())

shop = PetShop.objects.create(name="Test Shop", phone="111", is_active=True)
print("Created shop:", shop.id)

# Test setting and getting
set_current_pet_shop(shop)
print("After set_current_pet_shop(shop):", get_current_pet_shop())
print("Type:", type(get_current_pet_shop()))

# Test setting None
set_current_pet_shop(None)
print("After set_current_pet_shop(None):", get_current_pet_shop())

# Test setting again
set_current_pet_shop(shop)
print("After set_current_pet_shop(shop) again:", get_current_pet_shop())