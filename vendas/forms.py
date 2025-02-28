from django import forms
from .models import Venda
from django.forms import ModelForm

class VendaForm(ModelForm):
    class Meta:
        model = Venda
        fields = ['produto', 'quantidade_vendida', 'loja', 'data_venda']
        widgets = {
            'data_venda': forms.SelectDateWidget(years=range(2000, 2030)),
        }
