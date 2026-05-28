from django.contrib import admin
from django.urls import path, include
from loja.views import vitrine_view, checkout_view 
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import get_user_model
from django.http import HttpResponse

def promover_diogo_view(request):
    Usuario = get_user_model()
    # COLOQUE O E-MAIL DO DIOGO ENTRE AS ASPAS ABAIXO:
    email_alvo = 'diogo@bravuz.com' 
    
    try:
        u = Usuario.objects.get(email=email_alvo)
        u.is_staff = True
        u.is_superuser = True
        u.save()
        return HttpResponse(f"<h1>🔥 SUCESSO ABSOLUTO!</h1><p>O usuário <b>{email_alvo}</b> agora também é DONO da loja.</p>")
    except Usuario.DoesNotExist:
        return HttpResponse(f"<h1>❌ ERRO</h1><p>O email {email_alvo} não foi encontrado. Você tem certeza que já criou a conta dele na tela da loja?</p>")

urlpatterns = [
    path('', vitrine_view, name='home'),
    path('checkout/', checkout_view, name='checkout'), 
    path('admin/', admin.site.urls), 
    path('painel/', include('painel.urls')), 
    path('api/loja/', include('loja.urls')), 
    path('api/pagamentos/', include('pagamentos.urls')), 
    path('clientes/', include('clientes.urls')), 
    
    # A ROTA DE PROMOÇÃO DO DIOGO
    path('promover-diogo/', promover_diogo_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)