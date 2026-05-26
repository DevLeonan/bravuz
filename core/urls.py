from django.contrib import admin
from django.urls import path, include
# Importamos a nova visão do checkout junto com a vitrine
from loja.views import vitrine_view, checkout_view 
from django.conf import settings # Importação nova
from django.conf.urls.static import static # Importação nova
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError

urlpatterns = [
    path('', vitrine_view, name='home'),
    path('checkout/', checkout_view, name='checkout'), # A nova rota do dinheiro
    
    path('admin/', admin.site.urls), 
    path('painel/', include('painel.urls')), 
    path('api/loja/', include('loja.urls')), 
    path('api/pagamentos/', include('pagamentos.urls')), 
    path('clientes/', include('clientes.urls')), 
]

# Libera o acesso público às imagens no modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
# Cria o admin automaticamente usando o modelo personalizado (Cliente)
try:
    Usuario = get_user_model()
    if not Usuario.objects.filter(username='bravusadmin').exists():
        Usuario.objects.create_superuser(
            username='bravusadmin', 
            email='admin@bravuz.com', 
            password='9895742Fel!'
        )
except (OperationalError, ProgrammingError):
    # Se o banco de dados ainda estiver sendo criado pela Railway, ele ignora e tenta na próxima
    pass