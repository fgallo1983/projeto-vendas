from django.db import models
from django.contrib.auth.models import User, AbstractUser
import datetime
from django.conf import settings  # 🔹 Importa settings corretamente
import datetime

# Modelo Produto
class Produto(models.Model):
    nome = models.CharField(max_length=255)
    valor = models.FloatField()

    def __str__(self):
        return self.nome

# Modelo Loja
class Loja(models.Model):
    nome = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.nome} - {self.cidade}'

# Modelo de Venda
class Venda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    loja = models.ForeignKey('Loja', on_delete=models.CASCADE)
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quantidade_vendida = models.PositiveIntegerField()
    valor = models.FloatField()  
    data_venda = models.DateField()

    class Meta:
        unique_together = ('produto', 'vendedor', 'data_venda')  # Impede vendas duplicadas do mesmo produto na mesma data

    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade_vendida} unidades - {self.data_venda}"
    
    
# Modelo para Upload de Arquivo do Vendedor
class ArquivoVendedor(models.Model):
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Aponta para CustomUser
    arquivo = models.FileField(upload_to='arquivos_vendedores/')
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Data e hora do upload
    
    class Meta:
        verbose_name = "Arquivo vendendor"  # Nome singular
        verbose_name_plural = "Arquivo vendendores"  # Nome plural
    
    def __str__(self):
        return f"Arquivo de {self.vendedor.username} enviado em {self.uploaded_at.strftime('%d/%m/%Y %H:%M:%S')}"
    
class CustomUser(AbstractUser):
    lojas = models.ManyToManyField(Loja, blank=True)  # Agora é um ManyToManyField
    
    class Meta:
        verbose_name = "Vendedora"  # Nome singular
        verbose_name_plural = "Vendedoras"  # Nome plural

    def __str__(self):
        return f"{self.first_name} {self.last_name}"  # Retorna o nome completo do usuário
    
class MetaAcrescimo(models.Model):
    min_pecas = models.PositiveIntegerField("Mínimo de Peças")
    max_pecas = models.PositiveIntegerField("Máximo de Peças", blank=True, null=True)  # Pode ser null para o último intervalo
    acrescimo = models.FloatField("Valor do Acréscimo")

    class Meta:
        ordering = ["min_pecas"]  # Garante que os intervalos fiquem ordenados corretamente

    def __str__(self):
        max_pecas_display = f"até {self.max_pecas}" if self.max_pecas else "+"
        return f"{self.min_pecas} {max_pecas_display} peças → +R$ {self.acrescimo:.2f}"
