from rest_framework import serializers
from .models import Categoria, Produto

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.ReadOnlyField(source='categoria.nome')

    class Meta:
        model = Produto
        # Adicionamos o 'genero' na lista de campos exportados
        fields = [
            'id', 'categoria_nome', 'nome', 'descricao', 'preco', 
            'estoque', 'promocao_relampago', 'preco_promocional', 'imagem', 'genero'
        ]