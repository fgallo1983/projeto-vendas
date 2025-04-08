from django import forms
from vendas.models import Venda, Produto, Loja, ArquivoVendedor, CustomUser
import datetime


class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['produto', 'loja', 'quantidade_vendida', 'data_venda']

    produto = forms.ModelChoiceField(queryset=Produto.objects.all(), label="Produto")
    quantidade_vendida = forms.IntegerField(min_value=1, label="Quantidade")
    data_venda = forms.DateField(label="Data da Venda", widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        vendedor = kwargs.pop('vendedor', None)
        super().__init__(*args, **kwargs)

        if user and not user.is_staff:
            self.fields['loja'].queryset = user.lojas.all()
        else:
            self.fields['loja'].queryset = Loja.objects.all()

        if user and user.is_staff:
            self.fields['vendedor'] = forms.ModelChoiceField(
                queryset=CustomUser.objects.filter(is_staff=False),
                label="Vendedora"
            )

    def save(self, commit=True):
        venda = super().save(commit=False)
        if 'vendedor' in self.cleaned_data:
            venda.vendedor = self.cleaned_data['vendedor']
        if commit:
            venda.save()
        return venda

    
class RoteiroForm(forms.ModelForm):
    class Meta:
        model = ArquivoVendedor
        fields = ['vendedor', 'arquivo']
        
class EditarVendasForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['produto', 'quantidade_vendida']

