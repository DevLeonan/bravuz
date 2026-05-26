from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # As colunas que você vai ver ao listar os clientes no painel
    list_display = ('username', 'email', 'cpf', 'carteira_cashback', 'codigo_indicacao')
    # Permite pesquisar clientes pelo nome, email ou CPF
    search_fields = ('username', 'email', 'cpf')