from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from loja.models import Produto, Categoria
from pagamentos.models import Pedido, ItemPedido
from clientes.models import Cliente
from datetime import timedelta 
from django.core.files import File 
from decimal import Decimal, InvalidOperation
import csv
import io
import os 
import zipfile
import tempfile
import shutil

def checar_admin(user):
    return user.is_authenticated and user.is_staff

# ========================================================
# 1. DASHBOARD DE ALTA PERFORMANCE (CENTRAL DE INTELIGÊNCIA)
# ========================================================
@user_passes_test(checar_admin, login_url='/clientes/auth/')
def dashboard(request):
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    
    # Filtros de Pedidos Aprovados
    pedidos_hoje = Pedido.objects.filter(criado_em__date=hoje, status='aprovado')
    pedidos_mes = Pedido.objects.filter(criado_em__date__gte=inicio_mes, status='aprovado')
    
    # Métricas Financeiras Cruciais
    faturamento_hoje = pedidos_hoje.aggregate(Sum('valor_total'))['valor_total__sum'] or Decimal('0.00')
    faturamento_mes = pedidos_mes.aggregate(Sum('valor_total'))['valor_total__sum'] or Decimal('0.00')
    
    qtd_pedidos_hoje = pedidos_hoje.count()
    ticket_medio_hoje = (faturamento_hoje / qtd_pedidos_hoje) if qtd_pedidos_hoje > 0 else Decimal('0.00')
    
    # Métricas de Monitorização Operacional e Alertas Críticos
    total_clientes = Cliente.objects.filter(is_superuser=False).count()
    produtos_esgotados = Produto.objects.filter(estoque=0).count()
    estoque_critico = Produto.objects.filter(estoque__gt=0, estoque__lte=3).count()
    
    # Faturamento dos Últimos 7 Dias (Construção do Gráfico)
    dias_grafico = []
    valores_grafico = []
    for i in range(6, -1, -1):
        dia_alvo = hoje - timedelta(days=i)
        total_dia = Pedido.objects.filter(criado_em__date=dia_alvo, status='aprovado').aggregate(Sum('valor_total'))['valor_total__sum'] or Decimal('0.00')
        dias_grafico.append(dia_alvo.strftime('%d/%m'))
        valores_grafico.append(float(total_dia))

    # Ranking de Produtos Mais Vendidos (Análise de Volume)
    ranking_produtos = (
        ItemPedido.objects.filter(pedido__status='aprovado')
        .values('nome_produto', 'produto_id')
        .annotate(total_vendido=Count('id'))
        .order_by('-total_vendido')[:5]
    )

    pedidos_recentes = Pedido.objects.all().order_by('-criado_em')[:10]
    
    contexto = {
        'faturamento_hoje': faturamento_hoje,
        'faturamento_mes': faturamento_mes,
        'qtd_pedidos_hoje': qtd_pedidos_hoje,
        'ticket_medio_hoje': ticket_medio_hoje,
        'total_clientes': total_clientes,
        'produtos_esgotados': produtos_esgotados,
        'estoque_critico': estoque_critico,
        'labels_grafico': dias_grafico,
        'dados_grafico': valores_grafico,
        'ranking_produtos': ranking_produtos,
        'pedidos_recentes': pedidos_recentes,
    }
    return render(request, 'painel/dashboard.html', contexto)


# ========================================================
# 2. GESTÃO AVANÇADA DE PRODUTOS E AÇÕES EM MASSA
# ========================================================
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
            genero = request.POST.get('genero', 'U')
            tamanhos = request.POST.get('tamanhos', '')
            
            categoria = Categoria.objects.get(id=categoria_id)
            Produto.objects.create(
                nome=nome, preco=preco, estoque=estoque, genero=genero,
                categoria=categoria, descricao="Adicionado via Painel de Controlo",
                promocao_relampago=promocao_relampago, preco_promocional=preco_promocional,
                imagem=imagem, tamanhos=tamanhos
            )
            
        elif acao == 'editar':
            produto_id = request.POST.get('produto_id')
            produto = Produto.objects.get(id=produto_id)
            produto.nome = request.POST.get('nome')
            produto.preco = request.POST.get('preco')
            produto.estoque = request.POST.get('estoque', 0)
            produto.genero = request.POST.get('genero', produto.genero)
            produto.promocao_relampago = request.POST.get('promocao_relampago') == 'on'
            produto.preco_promocional = request.POST.get('preco_promocional') or None
            produto.tamanhos = request.POST.get('tamanhos', '')
            
            categoria_id = request.POST.get('categoria')
            produto.categoria = Categoria.objects.get(id=categoria_id)
            nova_imagem = request.FILES.get('imagem')
            if nova_imagem: 
                produto.imagem = nova_imagem
            produto.save()
            
        elif acao == 'deletar':
            produto_id = request.POST.get('produto_id')
            Produto.objects.filter(id=produto_id).delete()

        elif acao == 'limpar_catalogo':
            Produto.objects.all().delete()
            
        # SUPER FUNÇÃO: Alteração de Preços em Massa (Markup/Desconto por Categoria)
        elif acao == 'ajuste_em_massa':
            categoria_filter = request.POST.get('categoria_massa')
            tipo_ajuste = request.POST.get('tipo_ajuste') 
            porcentagem = Decimal(request.POST.get('porcentagem', 0)) / 100
            
            query_produtos = Produto.objects.all()
            if categoria_filter and categoria_filter != 'todas':
                query_produtos = query_produtos.filter(categoria_id=categoria_filter)
                
            for prod in query_produtos:
                if tipo_ajuste == 'aumentar':
                    prod.preco = prod.preco * (1 + porcentagem)
                    if prod.preco_promocional: 
                        prod.preco_promocional = prod.preco_promocional * (1 + porcentagem)
                elif tipo_ajuste == 'diminuir':
                    prod.preco = prod.preco * (1 - porcentagem)
                    if prod.preco_promocional: 
                        prod.preco_promocional = prod.preco_promocional * (1 - porcentagem)
                prod.save()
                
        # SUPER FUNÇÃO: Forçar Promoção Relâmpago em Bloco
        elif acao == 'promocao_em_massa':
            categoria_filter = request.POST.get('categoria_promo_massa')
            status_promo = request.POST.get('status_promo') == 'ativar'
            porcentagem_desc = Decimal(request.POST.get('desconto_promo', 0)) / 100
            
            query_produtos = Produto.objects.all()
            if categoria_filter and categoria_filter != 'todas':
                query_produtos = query_produtos.filter(categoria_id=categoria_filter)
                
            query_produtos.update(promocao_relampago=status_promo)
            
            if status_promo and porcentagem_desc > 0:
                for prod in query_produtos:
                    prod.preco_promocional = prod.preco * (1 - porcentagem_desc)
                    prod.save()

        # MOTOR DE IMPORTAÇÃO CONJUGADO ATUALIZADO (CSV + IMAGENS EM ZIP + TAMANHOS)
        elif acao == 'importar_csv':
            arquivo_csv = request.FILES.get('arquivo_csv')
            arquivo_zip = request.FILES.get('arquivo_zip')
            
            if arquivo_csv and arquivo_csv.name.endswith('.csv'):
                pasta_temp_extracao = None
                fotos_mapeadas = {}

                if arquivo_zip and arquivo_zip.name.endswith('.zip'):
                    pasta_temp_extracao = tempfile.mkdtemp()
                    try:
                        with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
                            zip_ref.extractall(pasta_temp_extracao)
                        for root, _, arquivos in os.walk(pasta_temp_extracao):
                            for arq in arquivos:
                                if arq.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                                    fotos_mapeadas[arq.lower()] = os.path.join(root, arq)
                    except Exception as erro_zip:
                        print(f"❌ Erro ao ler arquivo ZIP: {erro_zip}")

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
                            if ',' in preco_str and '.' in preco_str: 
                                preco_str = preco_str.replace('.', '')
                            preco_str = preco_str.replace(',', '.').strip()
                            nome_cat = linha[2].strip()
                            caminho_imagem_original = linha[3].strip() if len(linha) > 3 else ""
                            genero_csv = linha[4].strip().upper() if len(linha) > 4 else 'U'
                            estoque_csv = int(linha[5].strip()) if len(linha) > 5 and linha[5].strip().isdigit() else 10
                            
                            # Suporte para a 7ª coluna opcional de tamanhos na planilha Excel/CSV
                            tamanhos_csv = linha[6].strip() if len(linha) > 6 else ""
                            
                            if genero_csv not in ['M', 'F', 'U']: genero_csv = 'U'
                            
                            try:
                                preco_final = Decimal(preco_str)
                                if preco_final > Decimal('99999.00'): preco_final = Decimal('0.00')
                                
                                slug_cat = nome_cat.lower().strip().replace(' ', '-')
                                categoria, _ = Categoria.objects.get_or_create(slug=slug_cat, defaults={'nome': nome_cat.title()})
                                
                                produto_criado = Produto.objects.create(
                                    nome=nome_peca, preco=preco_final, categoria=categoria,
                                    estoque=estoque_csv, genero=genero_csv, tamanhos=tamanhos_csv, 
                                    descricao="Importado em lote via CSV"
                                )
                                
                                nome_arquivo_foto = os.path.basename(caminho_imagem_original).lower()
                                if nome_arquivo_foto in fotos_mapeadas:
                                    caminho_real_foto = fotos_mapeadas[nome_arquivo_foto]
                                    with open(caminho_real_foto, 'rb') as f:
                                        produto_criado.imagem.save(os.path.basename(caminho_real_foto), File(f), save=True)
                            except Exception as erro_linha:
                                print(f"❌ Erro na linha {linha_atual}: {erro_linha}")
                                continue
                finally:
                    if pasta_temp_extracao and os.path.exists(pasta_temp_extracao):
                        shutil.rmtree(pasta_temp_extracao)
                        
        return redirect('/painel/produtos/')

    filtro_estoque = request.GET.get('filtro_estoque')
    produtos = Produto.objects.all().order_by('-criado_em')
    
    if filtro_estoque == 'esgotados':
        produtos = produtos.filter(estoque=0)
    elif filtro_estoque == 'critico':
        produtos = produtos.filter(estoque__gt=0, estoque__lte=3)

    categorias = Categoria.objects.all()
    return render(request, 'painel/produtos.html', {'produtos': produtos, 'categorias': categorias})


# ========================================================
# 3. CONTROLO LOGÍSTICO E AUDITORIA DE ENCOMENDAS
# ========================================================
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

    filtro_status = request.GET.get('status')
    pedidos = Pedido.objects.all().order_by('-criado_em')
    if filtro_status in ['pendente', 'aprovado', 'recusado']:
        pedidos = pedidos.filter(status=filtro_status)

    return render(request, 'painel/pedidos.html', {'pedidos': pedidos})


# ========================================================
# 4. GESTÃO DE CLIENTES E PODER ABSOLUTO DE CASHBACK
# ========================================================
@user_passes_test(checar_admin, login_url='/clientes/auth/')
def gerenciar_clientes(request):
    if request.method == 'POST':
        acao = request.POST.get('acao')
        cliente_id = request.POST.get('cliente_id')
        cliente = get_object_or_404(Cliente, id=cliente_id)
        
        if acao == 'ajustar_cashback':
            novo_saldo = request.POST.get('carteira_cashback')
            try:
                cliente.carteira_cashback = Decimal(novo_saldo)
                cliente.save()
                return JsonResponse({'status': 'sucesso'})
            except (InvalidOperation, ValueError):
                return JsonResponse({'status': 'erro', 'mensagem': 'Valor inválido'}, status=400)
                
        elif acao == 'alternar_status_vip':
            cliente.is_staff = not cliente.is_staff 
            cliente.save()
            return JsonResponse({'status': 'sucesso', 'is_staff': cliente.is_staff})

    search_query = request.GET.get('busca_cliente', '')
    clientes = Cliente.objects.filter(is_superuser=False).annotate(
        total_pedidos=Count('pedido', filter=Q(pedido__status='aprovado')),
        total_gasto=Sum('pedido__valor_total', filter=Q(pedido__status='aprovado'))
    ).order_by('-total_gasto')

    if search_query:
        clientes = clientes.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) | 
            Q(cpf__icontains=search_query)
        )

    return render(request, 'painel/clientes.html', {'clientes': clientes, 'search_query': search_query})