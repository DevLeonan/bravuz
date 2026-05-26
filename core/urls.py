from django.contrib import admin
from django.urls import path, include
from loja.views import vitrine_view, checkout_view 
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import get_user_model
from django.http import HttpResponse

# Função hacker para forçar a criação do Admin
def forcar_admin_view(request):
    Usuario = get_user_model()
    try:
        # Verifica se já existe (usando o email, que costuma ser o padrão de e-commerces)
        if Usuario.objects.filter(email='admin@bravuz.com').exists():
            return HttpResponse("⚠️ O admin JÁ EXISTE. O login é o email: <b>admin@bravuz.com</b> e a senha: <b>SenhaForte2026</b>")
        
        # Tenta criar o superuser
        Usuario.objects.create_superuser(
            email='admin@bravuz.com', 
            password='SenhaForte2026',
            username='bravusadmin' # Passamos o username caso seu modelo ainda exija
        )
        return HttpResponse("✅ SUCESSO! Admin criado AGORA. O login é o email: <b>admin@bravuz.com</b> e a senha: <b>SenhaForte2026</b>")
    
    except Exception as erro:
        # Se o banco de dados recusar, ele vai mostrar o erro exato na tela!
        return HttpResponse(f"❌ DEU ERRO no banco de dados. O motivo foi: <br><br> <b>{str(erro)}</b>")

urlpatterns = [
    path('', vitrine_view, name='home'),
    path('checkout/', checkout_view, name='checkout'), 
    path('admin/', admin.site.urls), 
    path('painel/', include('painel.urls')), 
    path('api/loja/', include('loja.urls')), 
    path('api/pagamentos/', include('pagamentos.urls')), 
    path('clientes/', include('clientes.urls')), 
    
    # A nossa Rota Secreta
    path('criar-admin-secreto/', forcar_admin_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)