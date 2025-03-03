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
    
    data_venda = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today
    )
    
    def save(self, commit=True):
        venda = super().save(commit=False)
        
        # Extraímos o dia, mês e ano da data fornecida
        if self.cleaned_data['data_venda']:
            data_venda = self.cleaned_data['data_venda']
            venda.dia_venda = data_venda.day
            venda.mes_venda = data_venda.month
            venda.ano_venda = data_venda.year

        if commit:
            venda.vendedor = self.user  # Associar o vendedor logado à venda
            venda.save()
        
        return venda

