from django.contrib import admin
from django.urls import path, include
from loja.views import vitrine_view, checkout_view 
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import get_user_model
from django.http import HttpResponse

def promover_leonan_view(request):
    Usuario = get_user_model()
    try:
        # Puxa o usuário que você acabou de criar na loja
        u = Usuario.objects.get(email='dev.leonan@gmail.com')
        u.is_staff = True
        u.is_superuser = True
        u.save()
        return HttpResponse("<h1>🔥 SUCESSO ABSOLUTO!</h1><p>O usuário <b>dev.leonan@gmail.com</b> agora tem o poder de DEUS (Administrador) na loja. Vá para a tela de login normal e entre!</p>")
    except Usuario.DoesNotExist:
        return HttpResponse("<h1>❌ ERRO</h1><p>O email dev.leonan@gmail.com não foi encontrado no banco de dados.</p>")

urlpatterns = [
    path('', vitrine_view, name='home'),
    path('checkout/', checkout_view, name='checkout'), 
    path('admin/', admin.site.urls), 
    path('painel/', include('painel.urls')), 
    path('api/loja/', include('loja.urls')), 
    path('api/pagamentos/', include('pagamentos.urls')), 
    path('clientes/', include('clientes.urls')), 
    
    # A ROTA DE PROMOÇÃO
    path('promover-leonan/', promover_leonan_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)