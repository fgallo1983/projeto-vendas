from django.contrib import admin
from .models import Produto, Loja, Vendedor, Venda, ArquivoVendedor

admin.site.register(Produto)
admin.site.register(Loja)
admin.site.register(Vendedor)
admin.site.register(Venda)
admin.site.register(ArquivoVendedor)
