from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import VendaForm, RoteiroForm
from .models import Venda, ArquivoVendedor
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .models import ArquivoVendedor
from django.db.models import Sum
from django.contrib import messages
import datetime
from django.db.models import Min  # Importar para pegar o menor ID do grupo
from django.utils.timezone import now


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
def registrar_venda(request, venda_id=None):
    if request.method == 'POST':
        form = VendaForm(request.POST)
        if form.is_valid():
            venda = form.save(commit=False)
            
            # Verifica se já existe uma venda com a mesma data para o vendedor
            existe_venda = Venda.objects.filter(
                vendedor=request.user,
                data_venda=venda.data_venda
            ).exclude(id=venda_id).exists()

            if existe_venda:
                messages.error(request, "Você já cadastrou uma venda nessa data!")
            else:
                venda.vendedor = request.user  # Associa a venda ao vendedor logado
                venda.save()
                messages.success(request, "Venda cadastrada com sucesso!")  # Adiciona mensagem de sucesso

            return redirect('selos')  # Redireciona para a lista de vendas
    else:
        form = VendaForm()

    return render(request, 'registrar_venda.html', {'form': form})


# Verifica se o usuário é administrador
def is_admin(user):
    return user.is_staff  # Apenas administradores terão acesso

@user_passes_test(is_admin, login_url='/')  # Redireciona para o login se não for admin
def relatorio_vendas(request):
    
    today = datetime.date.today()
    mes_atual = today.month
    ano_atual = today.year
    
    # Lista de anos para o filtro (ajuste conforme necessário)
    anos_disponiveis = list(range(ano_atual, 2031))  # De ano_atual até 2030
    
    # Gerar uma lista de meses de Janeiro a Dezembro para cada ano
    meses_disponiveis = list(range(1, 13))  # Meses de 1 a 12 (Janeiro a Dezembro)
    
    # Pega o mês e o ano da URL (caso existam)
    mes = request.GET.get('mes', None)
    ano = request.GET.get('ano', None)
    
    # Caso os filtros sejam informados, converte para inteiros
    try:
        if mes:
            mes = int(mes)
        if ano:
            ano = int(ano)
    except ValueError:
        mes = None
        ano = None
    
    # Inicializa a queryset para vendas agrupadas por vendedor
    vendas_agrupadas = Venda.objects.values('vendedor', 'vendedor__first_name', 'vendedor__last_name') \
        .annotate(total_vendido=Sum('quantidade_vendida'))  # Soma da quantidade vendida por vendedor
    
    if ano:
        vendas_agrupadas = vendas_agrupadas.filter(data_venda__year=ano)
    if mes:
        vendas_agrupadas = vendas_agrupadas.filter(data_venda__month=mes)
        
    vendas_agrupadas = vendas_agrupadas.order_by('-total_vendido')  # Maior quantidade vendida primeiro
    
    # Inicializa a queryset para vendas agrupadas por loja
    vendas_por_loja = Venda.objects.values('loja', 'loja__nome') \
        .annotate(total_vendido=Sum('quantidade_vendida'))  # Soma da quantidade vendida por loja
    
    if ano:
        vendas_por_loja = vendas_por_loja.filter(data_venda__year=ano)
    if mes:
        vendas_por_loja = vendas_por_loja.filter(data_venda__month=mes)
        
    vendas_por_loja = vendas_por_loja.order_by('-total_vendido')  # Maior quantidade vendida primeiro
    
    # Passando os dados para o template
    context = {
        'vendas_agrupadas': vendas_agrupadas,
        'vendas_por_loja': vendas_por_loja,
        'mes': mes,
        'ano': ano,
        'mes_atual': mes_atual,
        'ano_atual': ano_atual,
        'anos_disponiveis': anos_disponiveis,  # Passa a lista de anos para o template
        'meses_disponiveis': meses_disponiveis,  # Lista de meses de Janeiro a Dezembro
    }

    return render(request, 'relatorio_vendas.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def pagina_roteiros(request):
    return render(request, 'roteiros.html')

@login_required
def enviar_roteiro(request):
    if request.method == "POST":
        form = RoteiroForm(request.POST, request.FILES)
        if form.is_valid():
            roteiro = form.save(commit=False)
            roteiro.data_upload = now()  # Define a data de upload automaticamente
            roteiro.save()
            messages.success(request, "Arquivo enviado com sucesso!")
            return redirect('enviar_roteiro')
        else:
            messages.error(request, "Falha ao enviar arquivo.")
    else:
        form = RoteiroForm()

    roteiros = ArquivoVendedor.objects.all().order_by('-uploaded_at')  # Ordena por data decrescente

    return render(request, 'enviar_roteiro.html', {'form': form, 'roteiros': roteiros})

@login_required
def excluir_roteiro(request, roteiro_id):
    try:
        roteiro = ArquivoVendedor.objects.get(id=roteiro_id)
        roteiro.delete()
        messages.success(request, "Arquivo excluído com sucesso!")
    except ArquivoVendedor.DoesNotExist:
        messages.error(request, "Arquivo não encontrado!")
    
    return redirect('enviar_roteiro')

@login_required
def selos(request):
    today = datetime.date.today()
    mes_atual = today.month
    ano_atual = today.year
    
    # Lista de anos para o filtro (ajuste conforme necessário)
    anos_disponiveis = list(range(ano_atual, 2031))  # De ano_atual até 2030
    
    # Gerar uma lista de meses de Janeiro a Dezembro para cada ano
    meses_disponiveis = list(range(1, 13))  # Meses de 1 a 12 (Janeiro a Dezembro)
    
    # Obter o ano e mês dos filtros ou usar o ano e mês atuais como padrão
    ano = request.GET.get('ano', ano_atual)  # Pega o ano do filtro ou usa o ano atual
    mes = request.GET.get('mes', mes_atual)  # Pega o mês do filtro ou usa o mês atual

    # Validar e garantir que o ano e mês são válidos
    try:
        ano = int(ano)
        mes = int(mes)
    except ValueError:
        ano = ano_atual
        mes = mes_atual
    
    # Agrupar as vendas por dia e loja, somando a quantidade vendida e pegando um ID qualquer (o menor)
    vendas = (
        Venda.objects.filter(
            vendedor=request.user,
            data_venda__month=mes,  # Corrigido para usar o mês filtrado
            data_venda__year=ano  # Corrigido para usar o ano filtrado
        )
        .values('data_venda', 'loja__nome')
        .annotate(
            total_vendido=Sum('quantidade_vendida'),
            venda_id=Min('id')  # Pegamos o menor ID representativo do grupo
        )
        .order_by('data_venda')
    )

    # Dicionário de tradução dos dias da semana
    dias_da_semana = {
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira',
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }

    # Criar uma lista de vendas com as datas formatadas
    vendas_formatadas = []
    for venda in vendas:
        data_venda = venda['data_venda']  # Acessa o valor como dicionário
        dia_semana = data_venda.strftime('%A')  # Retorna o nome do dia da semana em inglês
        dia_semana_pt = dias_da_semana.get(dia_semana, dia_semana)  # Traduz para o português

        vendas_formatadas.append({
            'id': venda['venda_id'],  # ✅ Pegando corretamente o ID representativo
            'data_venda': data_venda.strftime('%d/%m/%Y'),  # ✅ Acessando data corretamente
            'dia_semana': dia_semana_pt,
            'loja': venda['loja__nome'],  # ✅ Acessando nome da loja corretamente
            'quantidade_vendida': venda['total_vendido']  # ✅ Acessando total vendido corretamente
        })

    # Calcular o total vendido
    total_vendido = sum(venda['quantidade_vendida'] for venda in vendas_formatadas)

    # Passar o mês, ano e vendas ao template
    context = {
        'vendas': vendas_formatadas,
        'mes_atual': mes,  # Passa o mês filtrado para o template
        'ano_atual': ano,
        'total_vendido': total_vendido,
        'anos_disponiveis': anos_disponiveis,  # Passa a lista de anos para o template
        'meses_disponiveis': meses_disponiveis,  # Lista de meses de Janeiro a Dezembro
        'ano': ano,  # Passa o ano filtrado para o template
        'mes': mes,  # Passa o mês filtrado para o template
    }

    return render(request, 'selos.html', context)

@login_required
def editar_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id, vendedor=request.user)

    if request.method == "POST":
        form = VendaForm(request.POST, instance=venda)
        if form.is_valid():
            form.save()
            messages.success(request, "Venda editada com sucesso!")
            return redirect('selos')
    else:
        form = VendaForm(instance=venda)

    return render(request, 'editar_venda.html', {'form': form, 'venda': venda})



@login_required
def apagar_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id, vendedor=request.user)

    if request.method == "POST":
        venda.delete()
        messages.success(request, "Venda excluída com sucesso!")
        return redirect('selos')

    return render(request, 'confirmar_exclusao.html', {'venda': venda})