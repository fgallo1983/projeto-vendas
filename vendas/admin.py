from django.contrib import admin
from .models import Produto, Loja, Venda, ArquivoVendedor, CustomUser
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.db.models import Sum  # Importando o Sum para agregação


# Classe personalizada para o painel de administração
class CustomAdminSite(admin.AdminSite):
    site_header = 'Administração Lokenzzi'  # Título do cabeçalho
    site_title = 'Administração de Vendas Promotoras Lokenzzi'  # Título da aba no navegador
    index_title = 'Painel de Controle'  # Título na página inicial do admin

# Instância do admin personalizado
admin_site = CustomAdminSite(name='admin')

# Registra os modelos no admin personalizado
admin_site.register(Produto)
admin_site.register(Loja)
admin_site.register(ArquivoVendedor)

# Classe personalizada para o modelo CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    verbose_name_plural = "Vendedoras"  # Altera o nome plural para "Vendedores"
    # Personalizando a exibição no admin
    list_display = ('username', 'email', 'get_full_name', 'loja', 'is_staff', 'is_active')

    # Campos para pesquisa
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Ordenação padrão
    ordering = ['username']

    # Método para exibir o nome completo
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    get_full_name.short_description = 'Vendedora'  # Define o título da coluna

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('loja',)}),  # Adiciona o campo "loja" no formulário
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('loja',)}),  # Adiciona o campo "loja" no formulário de criação
    )

# Registra o modelo CustomUser com o administrador personalizado
admin_site.register(CustomUser, CustomUserAdmin)

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

    # quantidade_total_vendida.short_description = 'Total Vendido'
    
    def vendedor_nome_completo(self, obj):
        """Retorna o nome completo do vendedor"""
        return f"{obj.vendedor.first_name} {obj.vendedor.last_name}"  # Usando first_name e last_name do vendedor
    
    vendedor_nome_completo.short_description = 'Nome Completo do Vendedor'

# Registra o modelo Venda com o admin personalizado
admin_site.register(Venda, VendaAdmin)
