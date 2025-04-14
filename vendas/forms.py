from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from vendas.models import Venda, Produto, Loja, ArquivoVendedor, CustomUser, MetaAcrescimo
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

User = get_user_model()

class VendedoraForm(forms.ModelForm):
    email = forms.EmailField(label="E-mail / Username", required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "lojas", "is_active"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Garante que o username seja igual ao e-mail
        if commit:
            user.save()
            self.save_m2m()
        return user
    
class MetaAcrescimoForm(forms.ModelForm):
    class Meta:
        model = MetaAcrescimo
        fields = ["min_pecas", "max_pecas", "acrescimo"]

class OptionalSetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label="Nova senha", 
        widget=forms.PasswordInput, 
        required=False
    )
    new_password2 = forms.CharField(
        label="Confirme a nova senha", 
        widget=forms.PasswordInput, 
        required=False
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        # Só valida se um deles foi preenchido
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("As senhas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data.get("new_password1")
        if password:
            self.user.password = make_password(password)
            if commit:
                self.user.save()
        return self.user
