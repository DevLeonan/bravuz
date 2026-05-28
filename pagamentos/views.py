from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
import mercadopago
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Pedido, ItemPedido
from loja.models import Produto  # IMPORTANTE: Importando o Produto para dar baixa no estoque
from decimal import Decimal

class CriarPedidoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        valor_total = request.data.get('valor_total')
        usar_cashback = request.data.get('usar_cashback', False)
        
        itens_carrinho = request.data.get('itens', []) 

        if not valor_total or float(valor_total) <= 0 or not itens_carrinho:
            return Response({'erro': 'Carrinho vazio ou inválido'}, status=status.HTTP_400_BAD_REQUEST)

        valor_final = Decimal(str(valor_total))
        cliente = request.user
        
        if usar_cashback and cliente.carteira_cashback > 0:
            if cliente.carteira_cashback >= valor_final:
                desconto = valor_final - Decimal('1.00')
            else:
                desconto = cliente.carteira_cashback
                
            valor_final -= desconto
            cliente.carteira_cashback -= desconto
            cliente.save()

        pedido = Pedido.objects.create(
            cliente=cliente,
            valor_total=valor_final,
            status='pendente'
        )

        for item in itens_carrinho:
            ItemPedido.objects.create(
                pedido=pedido,
                produto_id=item['id'],
                nome_produto=item['nome'],
                preco_unitario=Decimal(str(item['preco'])),
                quantidade=1 
            )

        return Response({'pedido_id': pedido.id}, status=status.HTTP_201_CREATED)


class CriarPixView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user, status='pendente')
        
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        
        payment_data = {
            "transaction_amount": float(pedido.valor_total),
            "description": f"Bravuz - Pedido #{pedido.id}",
            "payment_method_id": "pix",
            "payer": {
                "email": pedido.cliente.email or "cliente@bravuz.com",
                "first_name": pedido.cliente.first_name or pedido.cliente.username,
                "last_name": pedido.cliente.last_name or "Silva",
                "identification": {
                    "type": "CPF",
                    "number": pedido.cliente.cpf or "00000000000" 
                }
            }
        }
        
        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]
        
        if "id" in payment:
            pedido.id_pagamento_mp = str(payment["id"])
            pedido.save()
            
            pix_copia_e_cola = payment["point_of_interaction"]["transaction_data"]["qr_code"]
            pix_qr_code_base64 = payment["point_of_interaction"]["transaction_data"]["qr_code_base64"]
            
            return Response({
                "status": "sucesso",
                "pedido_id": pedido.id,
                "pagamento_id_mp": pedido.id_pagamento_mp,
                "pix_copia_e_cola": pix_copia_e_cola,
                "pix_qr_code_base64": pix_qr_code_base64
            }, status=status.HTTP_201_CREATED)
            
        else:
            return Response({
                "status": "erro",
                "mensagem": "Não foi possível gerar o Pix junto ao intermediador."
            }, status=status.HTTP_400_BAD_REQUEST)


class VerificarStatusPagamentoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
        return Response({'status': pedido.status}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class WebhookMercadoPagoView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        data = request.data
        pagamento_id = data.get('data', {}).get('id') or data.get('id')
        
        if pagamento_id:
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(pagamento_id)
            
            if payment_info["status"] == 200:
                status_pagamento = payment_info["response"]["status"]
                
                try:
                    pedido = Pedido.objects.get(id_pagamento_mp=str(pagamento_id))
                    
                    if status_pagamento == 'approved':
                        if pedido.status != 'aprovado':
                            pedido.status = 'aprovado'
                            
                            # ==========================================
                            # MÁGICA 1: BAIXA AUTOMÁTICA DE ESTOQUE
                            # ==========================================
                            itens = ItemPedido.objects.filter(pedido=pedido)
                            for item in itens:
                                try:
                                    produto = Produto.objects.get(id=item.produto_id)
                                    if produto.estoque >= item.quantidade:
                                        produto.estoque -= item.quantidade
                                    else:
                                        produto.estoque = 0 # Evita que o estoque fique negativo
                                    produto.save()
                                except Produto.DoesNotExist:
                                    pass # Ignora se o produto tiver sido deletado do banco
                            
                            # ==========================================
                            # MÁGICA 2: DISTRIBUIÇÃO DE CASHBACK
                            # ==========================================
                            porcentagem_cashback = Decimal('0.05')
                            valor_cashback = pedido.valor_total * porcentagem_cashback
                            
                            cliente = pedido.cliente
                            cliente.carteira_cashback += valor_cashback
                            cliente.save()
                            
                            if cliente.indicado_por:
                                padrinho = cliente.indicado_por
                                padrinho.carteira_cashback += Decimal('10.00')
                                padrinho.save()
                    
                    elif status_pagamento in ['rejected', 'cancelled']:
                        pedido.status = 'recusado'
                        
                    pedido.save()
                    
                except Pedido.DoesNotExist:
                    pass

        return JsonResponse({'status': 'notificacao_processada'}, status=200)