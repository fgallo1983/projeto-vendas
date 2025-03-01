from django.db import models
from django.contrib.auth.models import User, AbstractUser
import datetime
from django.conf import settings  # 🔹 Importa settings corretamente

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
    mes_venda = models.IntegerField(choices=[(i, i) for i in range(1, 13)], default=datetime.date.today().month)  
    ano_venda = models.IntegerField(choices=[(i, i) for i in range(2020, 2031)], default=datetime.date.today().year)

    
    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade_vendida} unidades - {self.mes_venda}/{self.ano_venda}"
    
    
# Modelo para Upload de Arquivo do Vendedor
class ArquivoVendedor(models.Model):
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Aponta para CustomUser
    arquivo = models.FileField(upload_to='arquivos_vendedores/')
    data_upload = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Arquivo vendendor"  # Nome singular
        verbose_name_plural = "Arquivo vendendores"  # Nome plural
    
    def __str__(self):
        return f"Arquivo de {self.vendedor.username}"
    
class CustomUser(AbstractUser):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Vendedor"  # Nome singular
        verbose_name_plural = "Vendedores"  # Nome plural

    def __str__(self):
        return self.username
