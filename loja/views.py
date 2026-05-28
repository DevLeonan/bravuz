from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Categoria, Produto
from .serializers import CategoriaSerializer, ProdutoSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# ==========================================
# 1. API DA LOJA (O motor que o JS consulta)
# ==========================================

class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny] # Qualquer pessoa pode ver as categorias

class ProdutoViewSet(viewsets.ReadOnlyModelViewSet):
    # Mostra apenas os produtos que você marcou como "Ativo" no painel
    queryset = Produto.objects.filter(ativo=True) 
    serializer_class = ProdutoSerializer
    permission_classes = [AllowAny]
    
# ==========================================
# 2. TELAS DA LOJA (A vitrine e o checkout)
# ==========================================

def vitrine_view(request):
    return render(request, 'loja/index.html')
    
# Protegemos o checkout: se não estiver logado, o Django joga para a tela de Login
@login_required(login_url='/clientes/auth/')
def checkout_view(request):
    # Trava dupla: Verificação manual absoluta. Se for um fantasma/anônimo, expulsa para o login.
    if not request.user.is_authenticated:
        return redirect('/clientes/auth/')
        
    return render(request, 'loja/checkout.html')

@csrf_exempt
def calcular_frete(request, cep):
    # Remove qualquer traço que o cliente digitar
    cep_limpo = cep.replace('-', '').strip()
    
    if len(cep_limpo) != 8:
        return JsonResponse({'erro': 'CEP inválido'}, status=400)

    # Capta o valor total do carrinho que o JS pode enviar na URL (ex: /frete/01001000/?total=350.00)
    try:
        total_carrinho = float(request.GET.get('total', 0.0))
    except ValueError:
        total_carrinho = 0.0

    try:
        # Consulta a API gratuita do ViaCEP com limite de tempo (timeout de 5s) para não travar seu site
        resposta = requests.get(f'https://viacep.com.br/ws/{cep_limpo}/json/', timeout=5)
        dados_cep = resposta.json()
        
        if 'erro' in dados_cep:
            return JsonResponse({'erro': 'CEP não encontrado'}, status=404)
            
        uf = dados_cep.get('uf')
        endereco_formatado = f"{dados_cep.get('logradouro')}, {dados_cep.get('bairro')} - {dados_cep.get('localidade')}/{uf}"
        
        # 👑 REGRA DE OURO: Acima de 300 reais, frete grátis ignorando a região
        if total_carrinho >= 300.00:
            valor_frete = 0.00
            prazo = 'Frete Grátis (Acima de R$ 300)'
        else:
            # Tabela de Frete Inteligente da Bravus
            if uf == 'SP':
                valor_frete = 15.00
                prazo = '2 a 4 dias úteis'
            elif uf in ['RJ', 'MG', 'ES', 'PR', 'SC', 'RS']:
                valor_frete = 22.00
                prazo = '4 a 7 dias úteis'
            else:
                valor_frete = 35.00
                prazo = '7 a 12 dias úteis'
            
        return JsonResponse({
            'sucesso': True,
            'endereco': endereco_formatado,
            'valor_frete': valor_frete,
            'prazo': prazo
        })
        
    except requests.exceptions.RequestException:
        # 🛡️ TRAVA DE SEGURANÇA: ViaCEP caiu ou a Railway foi bloqueada.
        # NUNCA impedimos o cliente de comprar. O erro silencioso entra em ação.
        
        if total_carrinho >= 300.00:
            valor_frete_emergencia = 0.00
            prazo_emergencia = 'Frete Grátis (Acima de R$ 300)'
        else:
            valor_frete_emergencia = 28.50 # Frete fixo nacional de emergência (ajuste como preferir)
            prazo_emergencia = 'Prazo padrão nacional (7 a 12 dias úteis)'
            
        return JsonResponse({
            'sucesso': True,
            'endereco': 'Não conseguimos puxar a rua automaticamente. Por favor, digite seu endereço completo.',
            'valor_frete': valor_frete_emergencia,
            'prazo': prazo_emergencia
        })