from django.db import models
from django.contrib.auth.models import User

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

# Modelo Vendedor (associando a um usuário e a uma loja)
class Vendedor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

# Modelo de Venda
class Venda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    quantidade_vendida = models.PositiveIntegerField()  # Quantidade vendida pelo vendedor
    data_venda = models.DateField(auto_now_add=True)  # Captura a data automaticamente

    
    def __str__(self):
        return f'{self.produto.nome} vendido por {self.vendedor.username} em {self.data_venda}'



# Modelo para Upload de Arquivo do Vendedor
class ArquivoVendedor(models.Model):
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to='uploads/')
    data_upload = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Arquivo de {self.vendedor.nome}'

