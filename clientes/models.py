from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class Cliente(AbstractUser):
    # Dados essenciais para o e-commerce e Mercado Pago
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    
    # O Sistema de Retenção (Cashback)
    carteira_cashback = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # O Sistema de Viralização (Indicação)
    codigo_indicacao = models.CharField(max_length=20, unique=True, blank=True)
    indicado_por = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='indicados'
    )

    def save(self, *args, **kwargs):
        # Gera um código de indicação único automaticamente quando o cliente se cadastra
        if not self.codigo_indicacao:
            self.codigo_indicacao = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - Cashback: R$ {self.carteira_cashback}"