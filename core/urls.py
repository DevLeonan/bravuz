from django.contrib import admin
from django.urls import path, include
from loja.views import vitrine_view, checkout_view 
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import get_user_model
from django.http import HttpResponse

def criar_donos(request):
    Usuario = get_user_model()
    
    # Cria o Leonan
    if not Usuario.objects.filter(email='leonan@bravuz.com').exists():
        Usuario.objects.create_superuser(
            username='leonan_admin', 
            email='leonan@bravuz.com', 
            password='BravuzLeonan2026!'
        )
        
    # Cria o Diogo
    if not Usuario.objects.filter(email='diogo@bravuz.com').exists():
        Usuario.objects.create_superuser(
            username='diogo_admin', 
            email='diogo@bravuz.com', 
            password='BravuzDiogo2026!'
        )
        
    return HttpResponse("CONTAS DE DONO CRIADAS COM SUCESSO NO POSTGRES! Pode apagar este código, dar git push e fazer o login na loja.")

urlpatterns = [
    path('', vitrine_view, name='home'),
    path('checkout/', checkout_view, name='checkout'), 
    path('admin/', admin.site.urls), 
    path('painel/', include('painel.urls')), 
    path('api/loja/', include('loja.urls')), 
    path('api/pagamentos/', include('pagamentos.urls')), 
    path('clientes/', include('clientes.urls')), 
    path('forcar-admin/', criar_donos),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)