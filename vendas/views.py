from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import VendaForm, RoteiroForm
from .models import Venda, ArquivoVendedor, Produto, CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .models import ArquivoVendedor
from django.db.models import Sum
from django.contrib import messages
import datetime
from django.db.models import Min  # Importar para pegar o menor ID do grupo
from django.utils.timezone import now
import calendar


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
    if request.method == "POST":
        form = VendaForm(request.POST)
        if form.is_valid():
            venda = form.save(commit=False)
            venda.vendedor = request.user  # Associa a venda ao vendedor logado
            
            # Verifica se já existe uma venda para o mesmo produto na mesma data
            venda_existente = Venda.objects.filter(
                produto=venda.produto, data_venda=venda.data_venda, vendedor=venda.vendedor
            ).exists()

            if venda_existente:
                messages.error(request, "Você já cadastrou este produto nesta data!")
            else:
                venda.valor = venda.quantidade_vendida * venda.produto.valor  # Calcula o valor total
                venda.save()
                messages.success(request, "Venda registrada com sucesso!")
            
            return redirect('selos')

    else:
        form = VendaForm()

    vendas = Venda.objects.filter(vendedor=request.user).order_by('-data_venda')

    return render(request, "registrar_venda.html", {"form": form, "vendas": vendas})



# Verifica se o usuário é administrador
def is_admin(user):
    return user.is_staff  # Apenas administradores terão acesso

@user_passes_test(is_admin, login_url='/')  # Redireciona para o login se não for admin
def relatorio_vendas(request, id_vendedor=None):
    
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
    vendas_agrupadas = Venda.objects.select_related('vendedor') \
    .values('vendedor', 'vendedor__first_name', 'vendedor__last_name', 'vendedor__id') \
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
    
        # Se for admin e não houver id_vendedor, mostra todas as vendas de todos os vendedores
    if id_vendedor:  # Se o id_vendedor for fornecido, busca o vendedor específico
        vendedor = get_object_or_404(CustomUser, id=id_vendedor)
    else:  # Se não houver id_vendedor, mostra todas as vendas
        vendedor = None  # Isso significa que estamos considerando todos os vendedores

    # Filtra as vendas do vendedor selecionado
    vendas = Venda.objects.filter(vendedor=vendedor)
    
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
        'vendedor': vendedor, 
    }

    return render(request, 'relatorio_vendas.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def pagina_roteiros(request):
    
    roteiros = ArquivoVendedor.objects.filter(vendedor=request.user).order_by('-uploaded_at')
    return render(request, 'roteiros.html', {'roteiros': roteiros})

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
def selos(request, id_vendedor=None):
    # Se for admin e não houver id_vendedor, mostra todas as vendas de todos os vendedores
    if id_vendedor:
        if not request.user.is_staff:
            # Se o usuário não for staff, redireciona para a página inicial ou página de erro
            return redirect('home_vendedor')  # Ou página de erro, dependendo do seu fluxo

        # Se for staff, pode acessar qualquer vendedor
        vendedor = get_object_or_404(CustomUser, id=id_vendedor)
    else:
        # Caso não haja id_vendedor, é o próprio vendedor logado
        vendedor = request.user
    
    
    today = datetime.date.today()
    mes_atual = today.month
    ano_atual = today.year

    # Obtém os filtros de mês e ano, caso selecionados
    ano = int(request.GET.get('ano', ano_atual))
    mes = int(request.GET.get('mes', mes_atual))

    # Obtém todas as vendas do mês/ano filtrado
    vendas = Venda.objects.filter(data_venda__year=ano, data_venda__month=mes)

    # Obtém todos os produtos cadastrados
    produtos = Produto.objects.all()

    # Dicionário para armazenar vendas por dia e produto
    vendas_por_dia = {dia: {produto.id: 0 for produto in produtos} for dia in range(1, calendar.monthrange(ano, mes)[1] + 1)}

    # Popula o dicionário com os valores vendidos
    for venda in vendas:
        vendas_por_dia[venda.data_venda.day][venda.produto.id] = venda.quantidade_vendida
    
    # Calcula os totais de peças e valores
    total_por_produto = {produto.id: 0 for produto in produtos}
    valor_por_produto = {produto.id: 0 for produto in produtos}


    for venda in vendas:
        total_por_produto[venda.produto.id] += venda.quantidade_vendida

    # Soma total de peças vendidas no mês
    total_geral_pecas = sum(total_por_produto.values())

    # Define o acréscimo com base no total de peças vendidas
    if 501 <= total_geral_pecas <= 650:
        acrescimo = 0.25
    elif 651 <= total_geral_pecas <= 800:
        acrescimo = 0.50
    elif 801 <= total_geral_pecas <= 1000:
        acrescimo = 0.75
    elif total_geral_pecas > 1000:
        acrescimo = 1.00
    else:
        acrescimo = 0  # Sem alteração se for <= 500

    # Ajusta os valores dos produtos sem alterar o banco de dados
    for produto in produtos:
        preco_base = produto.valor or 0
        preco_final = preco_base + acrescimo
        valor_por_produto[produto.id] = total_por_produto[produto.id] * preco_final

    # Soma total dos valores
    total_geral_valor = sum(valor_por_produto.values())
    
    
    DIAS_SEMANA = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }

    dias_formatados = {
        dia: DIAS_SEMANA.get(datetime.date(ano, mes, dia).strftime("%A"), "Desconhecido")
        for dia in vendas_por_dia.keys()
    }

    return render(request, "selos.html", {
        "ano_atual": ano_atual,
        "mes_atual": mes_atual,
        "anos_disponiveis": list(range(ano_atual, 2031)),  # De ano_atual até 2030
        "meses_disponiveis": range(1, 13),
        "vendas_por_dia": vendas_por_dia,
        "produtos": produtos,
        "total_por_produto": total_por_produto,
        "valor_por_produto": valor_por_produto,
        "total_geral_pecas": total_geral_pecas,
        "total_geral_valor": total_geral_valor,
        "dias_formatados": dias_formatados,
        "ano": ano,  
        "mes": mes,  
        'vendedor': vendedor, 
    })

    
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