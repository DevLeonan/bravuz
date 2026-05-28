from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='painel_dashboard'),
    path('produtos/', views.gerenciar_produtos, name='painel_produtos'),
    path('pedidos/', views.gerenciar_pedidos, name='painel_pedidos'),
    path('clientes/', views.gerenciar_clientes, name='gerenciar_clientes'),
]