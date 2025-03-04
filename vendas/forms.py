from django import forms
from vendas.models import Venda, Produto, Loja
import datetime

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['produto', 'loja', 'quantidade_vendida', 'data_venda']

    produto = forms.ModelChoiceField(queryset=Produto.objects.all(), label="Produto")
    quantidade_vendida = forms.IntegerField(min_value=1, label="Quantidade")
    loja = forms.ModelChoiceField(queryset=Loja.objects.all(), label="Loja")
    data_venda = forms.DateField(label="Data da Venda", widget=forms.DateInput(attrs={'type': 'date'}))  # Novo campo para a data completa
    
    def save(self, commit=True):
        venda = super().save(commit=False)
        if commit:
            # venda.vendedor = self.user  # Associar o vendedor logado à venda
            venda.save()
        return venda

