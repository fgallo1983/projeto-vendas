from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import VendaForm
from .models import Venda
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from .models import ArquivoVendedor
from django.db.models import Sum


def index(request):
    # Se o usuário já estiver autenticado, redireciona para a página de vendas ou página inicial.
    if request.user.is_authenticated:
        return redirect('pagina_vendas')  # Ajuste para o nome da sua página de vendas

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # Realiza o login do usuário
            return redirect('pagina_vendas')  # Redireciona para a página de vendas após o login bem-sucedido
    else:
        form = AuthenticationForm()

    return render(request, 'index.html', {'form': form})

def pagina_vendas(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Redireciona para a página de login se o usuário não estiver autenticado
    
    arquivos = ArquivoVendedor.objects.filter(vendedor=request.user)  # ou outro critério
    return render(request, 'pagina_vendas.html', {'arquivos': arquivos})

@login_required
def registrar_venda(request):
    if request.method == 'POST':
        form = VendaForm(request.POST)
        if form.is_valid():
            venda = form.save(commit=False)
            venda.vendedor = request.user  # Associa a venda ao vendedor logado
            venda.save()
            return redirect('pagina_vendas')  # Redireciona para a lista de vendas
    else:
        form = VendaForm()
    
    return render(request, 'registrar_venda.html', {'form': form})

def relatorio_vendas(request):
    # Realizando a agregação para os dados de vendas
    vendas_por_vendedor = Venda.objects.values('vendedor__username', 'mes_venda', 'ano_venda').annotate(total_vendido=Sum('quantidade_vendida'))
    vendas_por_loja = Venda.objects.values('loja__nome', 'mes_venda', 'ano_venda').annotate(total_vendido=Sum('quantidade_vendida'))

    # Renderizando a página do relatório
    return render(request, 'relatorio_vendas.html', {
        'vendas_por_vendedor': vendas_por_vendedor,
        'vendas_por_loja': vendas_por_loja,
    })



