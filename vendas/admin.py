from django.contrib import admin
from .models import Produto, Loja, Vendedor, Venda, ArquivoVendedor

class VendaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'loja', 'vendedor', 'quantidade_vendida', 'mes_venda', 'ano_venda') 

admin.site.register(Produto)
admin.site.register(Loja)
admin.site.register(Vendedor)
admin.site.register(ArquivoVendedor)
admin.site.register(Venda, VendaAdmin)  # Registra o modelo de vendas com a visualização personalizada