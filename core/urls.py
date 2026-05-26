from django.contrib import admin
from django.urls import path, include
from loja.views import vitrine_view, checkout_view 
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import get_user_model
from django.http import HttpResponse

def forcar_admin_view(request):
    Usuario = get_user_model()
    try:
        if Usuario.objects.filter(email='admin@bravuz.com').exists():
            return HttpResponse("⚠️ O admin JÁ EXISTE. Faça o login com o email: <b>admin@bravuz.com</b> e a senha: <b>SenhaForte2026</b>")
        
        # Criamos o admin passando CPF e Telefone fictícios para passar na validação do seu modelo
        Usuario.objects.create_superuser(
            email='admin@bravuz.com', 
            password='SenhaForte2026',
            username='bravusadmin',
            cpf='03037190019',      # CPF fictício para destravar o banco
        )
        return HttpResponse("✅ SUCESSO! Admin criado com campos preenchidos. Login: <b>admin@bravuz.com</b> e senha: <b>SenhaForte2026</b>")
    
    except Exception as erro:
        return HttpResponse(f"❌ ERRO AO CRIAR: <br><br> <b>{str(erro)}</b>")

urlpatterns = [
    path('', vitrine_view, name='home'),
    path('checkout/', checkout_view, name='checkout'), 
    path('admin/', admin.site.urls), 
    path('painel/', include('painel.urls')), 
    path('api/loja/', include('loja.urls')), 
    path('api/pagamentos/', include('pagamentos.urls')), 
    path('clientes/', include('clientes.urls')), 
    
    path('criar-admin-secreto/', forcar_admin_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)