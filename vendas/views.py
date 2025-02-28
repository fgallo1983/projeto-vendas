from django.shortcuts import render, redirect
from .forms import VendaForm
from .models import Produto, Loja
from django.contrib.auth.decorators import login_required

@login_required
def registrar_venda(request):
    if request.method == 'POST':
        form = VendaForm(request.POST)
        if form.is_valid():
            venda = form.save(commit=False)
            venda.vendedor = request.user.vendedor
            venda.save()
            return redirect('venda_registrada')
    else:
        form = VendaForm()
    
    return render(request, 'registrar_venda.html', {'form': form})
