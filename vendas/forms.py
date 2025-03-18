from django import forms
from vendas.models import Venda, Produto, Loja, ArquivoVendedor
import datetime

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['produto', 'loja', 'quantidade_vendida', 'data_venda']

    produto = forms.ModelChoiceField(queryset=Produto.objects.all(), label="Produto")
    quantidade_vendida = forms.IntegerField(min_value=1, label="Quantidade")
    # loja = forms.ModelChoiceField(queryset=Loja.objects.all(), label="Loja")
    data_venda = forms.DateField(label="Data da Venda", widget=forms.DateInput(attrs={'type': 'date'}))  # Novo campo para a data completa
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pega o usuário do argumento
        super().__init__(*args, **kwargs)

        if user and not user.is_staff:  # Se for vendedora (não admin)
            self.fields['loja'].queryset = user.lojas.all()  # Filtra apenas as lojas da vendedora
        else:
            self.fields['loja'].queryset = Loja.objects.all()  # Admins veem todas as lojas
    
    def save(self, commit=True):
        venda = super().save(commit=False)
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

