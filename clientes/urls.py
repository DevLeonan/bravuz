from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('auth/', views.auth_view, name='auth'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('sair/', views.logout_view, name='logout'),
]