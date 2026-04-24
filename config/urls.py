from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # 🔓 PÚBLICO (sem slug)
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('publico/', include('publico.urls')),

    # 🔐 TENANT (com slug) - deve ser por último
    path('<slug:slug>/', include('core.tenant_urls')),
    path('<slug:slug>/tutores/', include('cadastro.urls')),
    path('<slug:slug>/agenda/', include('agenda.urls')),
    path('<slug:slug>/financeiro/', include('financeiro.urls')),
    path('<slug:slug>/prontuario/', include('prontuario.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)