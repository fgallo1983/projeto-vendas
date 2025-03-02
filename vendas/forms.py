from django import forms
from vendas.models import Venda, Produto, Loja

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['produto', 'loja', 'quantidade_vendida', 'mes_venda', 'ano_venda']

    produto = forms.ModelChoiceField(queryset=Produto.objects.all(), label="Produto")
    quantidade_vendida = forms.IntegerField(min_value=1, label="Quantidade")
    loja = forms.ModelChoiceField(queryset=Loja.objects.all(), label="Loja")
    
    def save(self, commit=True):
        # Adiciona automaticamente o vendedor (usuário logado)
        venda = super().save(commit=False)
        if commit:
            venda.vendedor = self.user  # Associar o vendedor logado à venda
            venda.save()
        return venda

