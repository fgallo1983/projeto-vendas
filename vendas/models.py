from django.db import models
from django.contrib.auth.models import User, AbstractUser
import datetime
from django.conf import settings  # 🔹 Importa settings corretamente
import datetime

# Modelo Produto
class Produto(models.Model):
    nome = models.CharField(max_length=255) 

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
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Aponta para CustomUser
    quantidade_vendida = models.PositiveIntegerField()  # Quantidade vendida pelo vendedor
    data_venda = models.DateField()  # Usamos uma única coluna para armazenar a data completa da venda

    
    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade_vendida} unidades - {self.data_venda}"
    
    
# Modelo para Upload de Arquivo do Vendedor
class ArquivoVendedor(models.Model):
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Aponta para CustomUser
    arquivo = models.FileField(upload_to='arquivos_vendedores/')
    
    class Meta:
        verbose_name = "Arquivo vendendor"  # Nome singular
        verbose_name_plural = "Arquivo vendendores"  # Nome plural
    
    def __str__(self):
        return f"Arquivo de {self.vendedor.username}"
    
class CustomUser(AbstractUser):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Vendedora"  # Nome singular
        verbose_name_plural = "Vendedoras"  # Nome plural

    def __str__(self):
        return f"{self.first_name} {self.last_name}"  # Retorna o nome completo do usuário
