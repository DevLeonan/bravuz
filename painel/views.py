from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from loja.models import Produto, Categoria
from pagamentos.models import Pedido
from clientes.models import Cliente
from datetime import timedelta 
from django.core.files import File 
from decimal import Decimal, InvalidOperation
import csv
import io
import os 

def checar_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(checar_admin, login_url='/clientes/auth/')
def dashboard(request):
    hoje = timezone.now().date()
    pedidos_hoje = Pedido.objects.filter(criado_em__date=hoje, status='aprovado')
    faturamento_hoje = pedidos_hoje.aggregate(Sum('valor_total'))['valor_total__sum'] or 0.00
    qtd_pedidos = pedidos_hoje.count()
    ticket_medio = (faturamento_hoje / qtd_pedidos) if qtd_pedidos > 0 else 0.00
    total_clientes = Cliente.objects.filter(is_superuser=False).count()

    dias_grafico = []
    valores_grafico = []
    for i in range(6, -1, -1):
        dia_alvo = hoje - timedelta(days=i)
        total_dia = Pedido.objects.filter(criado_em__date=dia_alvo, status='aprovado').aggregate(Sum('valor_total'))['valor_total__sum'] or 0.00
        dias_grafico.append(dia_alvo.strftime('%d/%m'))
        valores_grafico.append(float(total_dia))

    pedidos_recentes = Pedido.objects.all().order_by('-criado_em')[:5]
    contexto = {
        'faturamento_hoje': faturamento_hoje, 'qtd_pedidos': qtd_pedidos,
        'ticket_medio': ticket_medio, 'total_clientes': total_clientes,
        'labels_grafico': dias_grafico, 'dados_grafico': valores_grafico,
        'pedidos_recentes': pedidos_recentes,
    }
    return render(request, 'painel/dashboard.html', contexto)

@user_passes_test(checar_admin, login_url='/clientes/auth/')
def gerenciar_produtos(request):
    if request.method == 'POST':
        acao = request.POST.get('acao')
        
        if acao == 'criar':
            nome = request.POST.get('nome')
            preco = request.POST.get('preco')
            categoria_id = request.POST.get('categoria')
            promocao_relampago = request.POST.get('promocao_relampago') == 'on'
            preco_promocional = request.POST.get('preco_promocional') or None
            imagem = request.FILES.get('imagem')
            estoque = request.POST.get('estoque', 0)
            genero = request.POST.get('genero', 'U') # Padrão Unissex no manual
            
            categoria = Categoria.objects.get(id=categoria_id)
            
            Produto.objects.create(
                nome=nome, preco=preco, estoque=estoque, genero=genero,
                categoria=categoria, descricao="Adicionado via Painel Bravus",
                promocao_relampago=promocao_relampago, preco_promocional=preco_promocional,
                imagem=imagem
            )
            return redirect('/painel/produtos/')
            
        elif acao == 'deletar':
            produto_id = request.POST.get('produto_id')
            Produto.objects.filter(id=produto_id).delete()
            return redirect('/painel/produtos/')
            
        elif acao == 'editar':
            produto_id = request.POST.get('produto_id')
            produto = Produto.objects.get(id=produto_id)
            
            produto.nome = request.POST.get('nome')
            produto.preco = request.POST.get('preco')
            produto.estoque = request.POST.get('estoque', 0)
            produto.genero = request.POST.get('genero', produto.genero)
            produto.promocao_relampago = request.POST.get('promocao_relampago') == 'on'
            produto.preco_promocional = request.POST.get('preco_promocional') or None
            
            categoria_id = request.POST.get('categoria')
            produto.categoria = Categoria.objects.get(id=categoria_id)
            
            nova_imagem = request.FILES.get('imagem')
            if nova_imagem: produto.imagem = nova_imagem
                
            produto.save()
            return redirect('/painel/produtos/')

        elif acao == 'limpar_catalogo':
            Produto.objects.all().delete()
            return redirect('/painel/produtos/')
            
        elif acao == 'importar_csv':
            arquivo_csv = request.FILES.get('arquivo_csv')
            if arquivo_csv and arquivo_csv.name.endswith('.csv'):
                try:
                    try:
                        dataset = arquivo_csv.read().decode('utf-8-sig')
                    except UnicodeDecodeError:
                        arquivo_csv.seek(0)
                        dataset = arquivo_csv.read().decode('latin-1')
                        
                    io_string = io.StringIO(dataset)
                    primeira_linha = io_string.readline()
                    delimitador = ';' if ';' in primeira_linha else ','
                    io_string.seek(0)
                    next(io_string)
                    
                    linha_atual = 1
                    for linha in csv.reader(io_string, delimiter=delimitador, quotechar='"'):
                        linha_atual += 1
                        if len(linha) >= 3 and linha[0].strip():
                            nome_peca = linha[0].strip()
                            preco_str = linha[1].upper().replace('R$', '').replace(' ', '')
                            if ',' in preco_str and '.' in preco_str: preco_str = preco_str.replace('.', '')
                            preco_str = preco_str.replace(',', '.').strip()
                            nome_cat = linha[2].strip()
                            caminho_imagem = linha[3].strip() if len(linha) > 3 else ""
                            
                            # Captura o Gênero da 5ª coluna
                            genero_csv = linha[4].strip().upper() if len(linha) > 4 else 'U'
                            if genero_csv not in ['M', 'F', 'U']: genero_csv = 'U'
                            
                            try:
                                preco_final = Decimal(preco_str)
                                if preco_final > Decimal('99999.00'): preco_final = Decimal('0.00')
                                
                                slug_cat = nome_cat.lower().strip().replace(' ', '-')
                                categoria, _ = Categoria.objects.get_or_create(slug=slug_cat, defaults={'nome': nome_cat.title()})
                                
                                produto_criado = Produto.objects.create(
                                    nome=nome_peca, preco=preco_final, categoria=categoria,
                                    estoque=10, genero=genero_csv, descricao="Importado via CSV"
                                )
                                
                                if caminho_imagem and os.path.exists(caminho_imagem):
                                    with open(caminho_imagem, 'rb') as f:
                                        nome_arquivo_foto = os.path.basename(caminho_imagem)
                                        produto_criado.imagem.save(nome_arquivo_foto, File(f), save=True)
                                
                                print(f"✅ Sucesso na linha {linha_atual}: {nome_peca}")
                            except Exception as erro_linha:
                                print(f"❌ Erro na linha {linha_atual} ({nome_peca}): {erro_linha}")
                                continue
                except Exception as e:
                    print(f"🚨 ERRO FATAL: {e}")
            return redirect('/painel/produtos/')

    try:
        produtos = list(Produto.objects.all().order_by('-criado_em'))
    except InvalidOperation:
        Produto.objects.all().delete()
        produtos = []
        print("🚨 SISTEMA DE AUTOCURA ATIVADO: Catálogo expurgado.")

    categorias = Categoria.objects.all()
    return render(request, 'painel/produtos.html', {'produtos': produtos, 'categorias': categorias})

@user_passes_test(checar_admin, login_url='/clientes/auth/')
def gerenciar_pedidos(request):
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        novo_status = request.POST.get('status')
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            if novo_status in ['pendente', 'aprovado', 'recusado']:
                pedido.status = novo_status
                pedido.save()
                return JsonResponse({'status': 'sucesso'})
        except Pedido.DoesNotExist:
            return JsonResponse({'status': 'erro'}, status=400)

    pedidos = Pedido.objects.all().order_by('-criado_em')
    return render(request, 'painel/pedidos.html', {'pedidos': pedidos})