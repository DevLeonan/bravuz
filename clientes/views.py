from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Cliente
from pagamentos.models import Pedido # Importamos os pedidos para mostrar no histórico

def auth_view(request):
    if request.user.is_authenticated:
        return redirect('clientes:perfil')

    if request.method == 'POST':
        acao = request.POST.get('acao')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        if acao == 'login':
            user = authenticate(request, username=email, password=senha)
            if user is not None:
                login(request, user)
                return redirect('clientes:perfil')
            else:
                return render(request, 'clientes/auth.html', {'erro': 'Credenciais inválidas.'})
                
        elif acao == 'cadastro':
            cpf = request.POST.get('cpf', '')
            codigo_padrinho = request.POST.get('codigo_indicacao', '').strip()
            
            if not Cliente.objects.filter(username=email).exists():
                # Tenta encontrar quem indicou esse novo cliente
                padrinho = None
                if codigo_padrinho:
                    try:
                        padrinho = Cliente.objects.get(codigo_indicacao=codigo_padrinho)
                    except Cliente.DoesNotExist:
                        pass # Se o código for inválido, apenas ignora e cadastra normal
                
                # Cria o novo cliente já conectando ao padrinho (se houver)
                user = Cliente.objects.create_user(
                    username=email, 
                    email=email, 
                    password=senha, 
                    cpf=cpf,
                    indicado_por=padrinho
                )
                login(request, user)
                return redirect('clientes:perfil')
            else:
                return render(request, 'clientes/auth.html', {'erro': 'E-mail já cadastrado.'})
    
    # Se na URL tiver ?ref=CODIGO, nós pegamos para preencher o formulário automaticamente
    codigo_url = request.GET.get('ref', '')
    return render(request, 'clientes/auth.html', {'codigo_url': codigo_url})

@login_required(login_url='/clientes/auth/')
def perfil_view(request):
    # Busca todos os pedidos do cliente, do mais novo pro mais velho
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-criado_em')
    return render(request, 'clientes/perfil.html', {'pedidos': pedidos})

def logout_view(request):
    logout(request)
    return redirect('home')