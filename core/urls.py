from django.contrib import admin
from django.urls import path, include
from loja.views import vitrine_view, checkout_view 
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import get_user_model
from django.http import HttpResponse

def criar_socios_view(request):
    Usuario = get_user_model()
    mensagem = ""
    
    # 1. Cria a conta do Leonan
    if not Usuario.objects.filter(email='leonan@bravuz.com').exists():
        Usuario.objects.create_superuser(
            email='leonan@bravuz.com', 
            password='BravuzLeonan2026!', 
            username='leonan_admin', 
            cpf='11111111111', 
            telefone='51999999991'
        )
        mensagem += "✅ Conta de DONO criada para: <b>Leonan</b> (leonan@bravuz.com)<br>"
    else:
        mensagem += "⚠️ Conta do Leonan já existe.<br>"

    # 2. Cria a conta do Diogo
    if not Usuario.objects.filter(email='diogo@bravuz.com').exists():
        Usuario.objects.create_superuser(
            email='diogo@bravuz.com', 
            password='BravuzDiogo2026!', 
            username='diogo_admin', 
            cpf='22222222222', 
            telefone='51999999992'
        )
        mensagem += "✅ Conta de DONO criada para: <b>Diogo</b> (diogo@bravuz.com)<br>"
    else:
        mensagem += "⚠️ Conta do Diogo já existe.<br>"

    return HttpResponse(f"{mensagem}<br><br><b>🚨 SUCESSO! Agora APAGUE essa função do código para blindar a loja!</b>")

urlpatterns = [
    path('', vitrine_view, name='home'),
    path('checkout/', checkout_view, name='checkout'), 
    path('admin/', admin.site.urls), 
    path('painel/', include('painel.urls')), 
    path('api/loja/', include('loja.urls')), 
    path('api/pagamentos/', include('pagamentos.urls')), 
    path('clientes/', include('clientes.urls')), 
    
    # Rota temporária para criar os dois sócios
    path('criar-socios/', criar_socios_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)