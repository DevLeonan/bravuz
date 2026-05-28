from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True) # URL amigável (ex: /camisetas)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    # 1. Crie as opções de gênero
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('U', 'Unissex'),
    ]
    
    categoria = models.ForeignKey(Categoria, related_name='produtos', on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    
    # 2. O campo de gênero inserido junto com as outras informações
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, default='U')
    
    # ==========================================
    # NOVO CAMPO: Tamanhos Disponíveis
    # ==========================================
    tamanhos = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Digite os tamanhos separados por vírgula. Ex: P, M, G, GG ou 38, 40, 42"
    )
    
    # Preços e Estoque
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField(default=0)
    
    # Gatilhos de Venda
    ativo = models.BooleanField(default=True, help_text="Desmarque para ocultar o produto da loja")
    promocao_relampago = models.BooleanField(default=False)
    preco_promocional = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Imagem principal
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome