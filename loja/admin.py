from django.contrib import admin
from .models import Categoria, Produto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nome',)}

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'estoque', 'ativo', 'promocao_relampago')
    list_editable = ('preco', 'estoque', 'ativo', 'promocao_relampago')
    list_filter = ('ativo', 'categoria', 'promocao_relampago')
    search_fields = ('nome',)