from django.contrib import admin
from .models import Produto, Loja, Vendedor, Venda, ArquivoVendedor

class VendaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'vendedor', 'loja', 'quantidade_vendida', 'data_venda')  # Campos a serem exibidos na listagem

admin.site.register(Produto)
admin.site.register(Loja)
admin.site.register(Vendedor)
admin.site.register(ArquivoVendedor)
admin.site.register(Venda, VendaAdmin)  # Registra o modelo de vendas com a visualização personalizada