from django.contrib import admin
from .models import Produto, Loja, Venda, ArquivoVendedor, CustomUser
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.db.models import Sum  # Importando o Sum para agregação


# Registra os modelos padrões de forma simples

admin.site.register(Produto)
admin.site.register(Loja)
admin.site.register(ArquivoVendedor)

# Classe personalizada para o modelo CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    verbose_name_plural = "Vendedores"  # Altera o nome plural para "Vendedores"
    list_display = ['username', 'email', 'is_staff', 'is_active', 'loja']
    search_fields = ['username', 'email']
    ordering = ['username']

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('loja',)}),  # Adiciona o campo "loja" no formulário
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('loja',)}),  # Adiciona o campo "loja" no formulário de criação
    )

# Registra o modelo CustomUser com o administrador personalizado
admin.site.register(CustomUser, CustomUserAdmin)

# Classe personalizada para o modelo Venda
class VendaAdmin(admin.ModelAdmin):
    list_display = ('vendedor', 'loja', 'mes_venda', 'ano_venda', 'quantidade_total_vendida')
    list_filter = ('vendedor', 'loja', 'mes_venda', 'ano_venda')  # Filtros no admin
    ordering = ['ano_venda', 'mes_venda']  # Ordenação padrão

    def quantidade_total_vendida(self, obj):
        """Retorna a soma das quantidades vendidas por vendedor no mês"""
        total = Venda.objects.filter(
            vendedor=obj.vendedor,
            mes_venda=obj.mes_venda,
            ano_venda=obj.ano_venda
        ).aggregate(total=Sum('quantidade_vendida'))['total']
        
        return total or 0  # Retorna 0 se não houver vendas

    quantidade_total_vendida.short_description = 'Total Vendido'

# Registra o modelo Venda com o admin personalizado
admin.site.register(Venda, VendaAdmin)
