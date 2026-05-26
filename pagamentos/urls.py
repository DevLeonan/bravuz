from django.urls import path
from .views import CriarPixView, WebhookMercadoPagoView, CriarPedidoView, VerificarStatusPagamentoView

app_name = 'pagamentos'

urlpatterns = [
    # Rota que o Checkout chama para montar a caixa
    path('criar-pedido/', CriarPedidoView.as_view(), name='criar_pedido'),
    
    # Rota que o Checkout chama para gerar o QR Code
    path('criar-pix/<int:pedido_id>/', CriarPixView.as_view(), name='criar_pix'),
    
    # NOVO: Rota que o Checkout fica escutando para ver se o PIX caiu
    path('status/<int:pedido_id>/', VerificarStatusPagamentoView.as_view(), name='status_pagamento'),
    
    # Rota secreta que o robô do Mercado Pago acessa
    path('webhook/mercadopago/', WebhookMercadoPagoView.as_view(), name='webhook_mp'),
]