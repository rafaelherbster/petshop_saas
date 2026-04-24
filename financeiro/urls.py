from django.urls import path

from financeiro.views import edit_payment, payment_quick_status, register_payment

urlpatterns = [
    path('pagamento/<int:appointment_id>/', register_payment, name='register_payment'),
    path('pagamento/editar/<int:pk>/', edit_payment, name='edit_payment'),
    path('pagamento/status/<int:pk>/', payment_quick_status, name='payment_quick_status'),
]
