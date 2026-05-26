from django.db import models
from clientes.models import Cliente
from decimal import Decimal
from loja.models import Produto


class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pendente')
    
    # Trava de segurança: garante que o cashback só seja pago uma vez
    recompensa_processada = models.BooleanField(default=False) 
    id_pagamento_mp = models.CharField(max_length=255, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # A Mágica: Se o pedido mudou para pago e o dinheiro ainda não foi distribuído...
        if self.status == 'aprovado' and not self.recompensa_processada:
            
            # 1. Calcula e deposita 5% de cashback para o comprador
            cashback = self.valor_total * Decimal('0.05')
            self.cliente.carteira_cashback += cashback
            
            # 2. Regra de Indicação: Verifica se alguém indicou este cliente
            if self.cliente.indicado_por:
                # Confirma se é realmente a PRIMEIRA compra aprovada dele
                compras_aprovadas = Pedido.objects.filter(cliente=self.cliente, status='aprovado').count()
                if compras_aprovadas == 0: 
                    # Deposita R$ 10,00 na conta do padrinho que o indicou!
                    self.cliente.indicado_por.carteira_cashback += Decimal('10.00')
                    self.cliente.indicado_por.save()
            
            # Salva o saldo novo do comprador
            self.cliente.save()
            
            # Tranca o cofre para este pedido não gerar mais recompensas
            self.recompensa_processada = True 

        # Salva o pedido normalmente no banco de dados
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.email}"
 
class ItemPedido(models.Model):
    # Liga este item ao pedido principal
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE)
    
    # Se você deletar o produto da loja no futuro, o histórico do pedido não quebra
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    nome_produto = models.CharField(max_length=200) 
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"1x {self.nome_produto} (Pedido #{self.pedido.id})"