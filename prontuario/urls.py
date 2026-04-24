from django.urls import path

from prontuario.views import (
    health_record_create, health_record_delete, health_record_edit,
)

urlpatterns = [
    path('novo/', health_record_create, name='health_record_create'),
    path('<int:pk>/editar/', health_record_edit, name='health_record_edit'),
    path('<int:pk>/deletar/', health_record_delete, name='health_record_delete'),
]
