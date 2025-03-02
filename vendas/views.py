from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import VendaForm
from .models import Venda
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from .models import ArquivoVendedor
from django.db.models import Sum
from django.contrib.auth.decorators import user_passes_test


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



# def relatorio_vendas(request):
#     mes = request.GET.get('mes', None)
#     ano = request.GET.get('ano', None)
    
#     vendas_por_vendedor = Venda.objects.values('vendedor__first_name', 'vendedor__last_name', 'mes_venda', 'ano_venda') \
#         .filter(mes_venda=mes, ano_venda=ano) if mes and ano else Venda.objects.values('vendedor__first_name', 'vendedor__last_name', 'mes_venda', 'ano_venda') \
#         .annotate(total_vendido=Sum('quantidade_vendida'))
    
#     vendas_por_loja = Venda.objects.values('loja__nome', 'mes_venda', 'ano_venda') \
#         .filter(mes_venda=mes, ano_venda=ano) if mes and ano else Venda.objects.values('loja__nome', 'mes_venda', 'ano_venda') \
#         .annotate(total_vendido=Sum('quantidade_vendida'))

#     return render(request, 'relatorio_vendas.html', {
#         'vendas_por_vendedor': vendas_por_vendedor,
#         'vendas_por_loja': vendas_por_loja,
#         'mes': mes,
#         'ano': ano,
#     })