from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import VendaForm
from .models import Venda
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .models import ArquivoVendedor
from django.db.models import Sum
from django.contrib.auth.decorators import user_passes_test

def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('home_adm')
        else:
            return redirect('home_vendedor')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home_adm' if user.is_staff else 'home_vendedor')

    else:
        form = AuthenticationForm()

    return render(request, 'index.html', {'form': form})

@login_required
def home_vendedor(request):
    return render(request, 'home_vendedor.html')

@login_required
def home_adm(request):
    return render(request, 'home_adm.html')


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


# Verifica se o usuário é administrador
def is_admin(user):
    return user.is_staff  # Apenas administradores terão acesso

@user_passes_test(is_admin, login_url='/')  # Redireciona para o login se não for admin
def relatorio_vendas(request):
    
    mes = request.GET.get('mes', None)
    ano = request.GET.get('ano', None)
    
    vendas_agrupadas = Venda.objects.values('vendedor', 'vendedor__first_name', 'vendedor__last_name', 'mes_venda', 'ano_venda') \
        .annotate(total_vendido=Sum('quantidade_vendida'))  # Calcula o total de vendas por vendedor
        
    if mes and ano:
        # Adiciona os filtros de mês e ano
        vendas_agrupadas = vendas_agrupadas.filter(mes_venda=mes, ano_venda=ano)
    elif mes:
        # Adiciona apenas o filtro de mês, caso o ano não tenha sido fornecido
        vendas_agrupadas = vendas_agrupadas.filter(mes_venda=mes)
    elif ano:
        # Adiciona apenas o filtro de ano, caso o mês não tenha sido fornecido
        vendas_agrupadas = vendas_agrupadas.filter(ano_venda=ano)
        
        # Agregar vendas por loja e mês/ano
        
    vendas_por_loja = Venda.objects.values('loja', 'loja__nome', 'mes_venda', 'ano_venda') \
        .annotate(total_vendido=Sum('quantidade_vendida'))  # Calcula o total de vendas por loja
        
    if mes and ano:
        # Adiciona os filtros de mês e ano
        vendas_por_loja = vendas_por_loja.filter(mes_venda=mes, ano_venda=ano)
    elif mes:
        # Adiciona apenas o filtro de mês, caso o ano não tenha sido fornecido
        vendas_por_loja = vendas_por_loja.filter(mes_venda=mes)
    elif ano:
        # Adiciona apenas o filtro de ano, caso o mês não tenha sido fornecido
        vendas_por_loja = vendas_por_loja.filter(ano_venda=ano)

    return render(request, 'relatorio_vendas.html', {'vendas_agrupadas': vendas_agrupadas, 'vendas_por_loja': vendas_por_loja, 'mes': mes, 'ano': ano,})

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def pagina_roteiros(request):
    return render(request, 'roteiros.html')

@login_required
def enviar_roteiro(request):
    return render(request, 'enviar_roteiro.html')
