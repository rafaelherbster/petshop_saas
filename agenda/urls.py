from django.urls import path

from agenda.views import (
    appointment_create, appointment_delete, appointment_detail,
    appointment_edit, appointment_list, appointment_quick_status,
    service_create, service_edit, service_list, service_delete,
)

urlpatterns = [
    path('', appointment_list, name='appointment_list'),
    path('novo/', appointment_create, name='appointment_create'),
    path('<int:pk>/', appointment_detail, name='appointment_detail'),
    path('<int:pk>/editar/', appointment_edit, name='appointment_edit'),
    path('<int:pk>/deletar/', appointment_delete, name='appointment_delete'),
    path('<int:pk>/status/', appointment_quick_status, name='appointment_quick_status'),
    path('servicos/', service_list, name='service_list'),
    path('servicos/novo/', service_create, name='service_create'),
    path('servicos/<int:pk>/editar/', service_edit, name='service_edit'),
    path('servicos/<int:pk>/deletar/', service_delete, name='service_delete'),
]
