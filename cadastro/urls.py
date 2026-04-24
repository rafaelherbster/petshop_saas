from django.urls import path

from cadastro.views import (
    pet_create, pet_delete, pet_detail, pet_edit, pet_list,
    tutor_create, tutor_delete, tutor_detail, tutor_edit, tutor_list,
    loyalty_activate, loyalty_redeem,
)

urlpatterns = [
    path('', tutor_list, name='tutor_list'),
    path('novo/', tutor_create, name='tutor_create'),
    path('<int:pk>/', tutor_detail, name='tutor_detail'),
    path('<int:pk>/editar/', tutor_edit, name='tutor_edit'),
    path('<int:pk>/deletar/', tutor_delete, name='tutor_delete'),
    path('-animais/', pet_list, name='pet_list'),
    path('-animais/novo/', pet_create, name='pet_create'),
    path('-animais/<int:pk>/', pet_detail, name='pet_detail'),
    path('-animais/<int:pk>/editar/', pet_edit, name='pet_edit'),
    path('-animais/<int:pk>/deletar/', pet_delete, name='pet_delete'),
    path('-animais/<int:pk>/fidelidade/', loyalty_activate, name='loyalty_activate'),
    path('-animais/fidelidade/<int:pk>/resgatar/', loyalty_redeem, name='loyalty_redeem'),
]
