from django.contrib import admin
from django.urls import path, include
from loja.views import vitrine_view, checkout_view 
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from django.http import HttpResponse

def forcar_admin_view(request):
    Usuario = get_user_model()
    
    # 1. Tenta achar o admin. Se não achar, cria.
    user = Usuario.objects.filter(email='admin@bravuz.com').first()
    
    if not user:
        try:
            user = Usuario.objects.create_superuser(
                email='admin@bravuz.com', 
                password='SenhaForte2026',
                username='bravusadmin',
                cpf='00000000000',
                telefone='51999999999'
            )
        except Exception as erro:
            return HttpResponse(f"❌ ERRO NO BANCO: <br><br> <b>{str(erro)}</b>")

    # 2. MÁGICA: Faz o login forçado nos bastidores
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    # 3. Arremessa você direto para a página de produtos já logado!
    return redirect('/painel/produtos/')

urlpatterns = [
    path('', vitrine_view, name='home'),
    path('checkout/', checkout_view, name='checkout'), 
    path('admin/', admin.site.urls), 
    path('painel/', include('painel.urls')), 
    path('api/loja/', include('loja.urls')), 
    path('api/pagamentos/', include('pagamentos.urls')), 
    path('clientes/', include('clientes.urls')), 
    
    # A Rota do Auto-Login
    path('entrar-marreta/', forcar_admin_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)