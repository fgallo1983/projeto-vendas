from django.contrib import admin
from .models import Produto, Loja, Venda, ArquivoVendedor, CustomUser 
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

class VendaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'loja', 'vendedor', 'quantidade_vendida', 'mes_venda', 'ano_venda') 
    
    # Adicionando filtros para vendedor, loja, mês e ano
    list_filter = ('vendedor', 'loja', 'mes_venda', 'ano_venda')

    # Se você quiser permitir que o filtro funcione em outros campos (opcional)
    search_fields = ('vendedor__username', 'loja__nome', 'produto__nome')
    
# Verifique se o modelo já está registrado antes de tentar desregistrar
if not admin.site.is_registered(CustomUser):
    class CustomUserAdmin(UserAdmin):
        model = CustomUser
        verbose_name_plural = "Vendedores"  # Altera o nome plural para "Vendedores"
        list_display = ['username', 'email', 'is_staff', 'is_active', 'loja']  # Exemplo de campos que você quer exibir
        search_fields = ['username', 'email']
        ordering = ['username']

        # Personalize as seções do formulário de criação e atualização
        fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('loja',)}),  # Adicione campos personalizados
        )
        add_fieldsets = UserAdmin.add_fieldsets + (
            (None, {'fields': ('loja',)}),  # Adicione campos personalizados ao formulário de criação
        )

admin.site.register(Produto)
admin.site.register(Loja)
admin.site.register(ArquivoVendedor)
admin.site.register(Venda, VendaAdmin)  # Registra o modelo de vendas com a visualização personalizada
admin.site.register(CustomUser, CustomUserAdmin)