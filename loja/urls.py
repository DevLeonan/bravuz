from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ProdutoViewSet, calcular_frete

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'produtos', ProdutoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Nova rota de logística
    path('frete/<str:cep>/', calcular_frete, name='calcular_frete'),
]