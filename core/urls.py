from django.contrib import admin
from django.urls import path, include
# Importamos a nova visão do checkout junto com a vitrine
from loja.views import vitrine_view, checkout_view 
from django.conf import settings # Importação nova
from django.conf.urls.static import static # Importação nova
from django.contrib.auth.models import User

urlpatterns = [
    path('', vitrine_view, name='home'),
    path('checkout/', checkout_view, name='checkout'), # A nova rota do dinheiro
    
    path('admin/', admin.site.urls), 
    path('painel/', include('painel.urls')), 
    path('api/loja/', include('loja.urls')), 
    path('api/pagamentos/', include('pagamentos.urls')), 
    path('clientes/', include('clientes.urls')), 
]

# NOVO: Libera o acesso público às imagens no modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    
# Cria o admin automaticamente se ele não existir
if not User.objects.filter(username='bravusadmin').exists():
    User.objects.create_superuser('bravusadmin', 'admin@bravuz.com', '9895742Fel!')