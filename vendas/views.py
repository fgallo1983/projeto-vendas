import datetime
import calendar
from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, get_user_model
from django.db.models import Sum, Min, Max, Value
from django.db.models.functions import Concat
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.views import PasswordResetView 
from django.urls import reverse_lazy

from .forms import VendaForm, RoteiroForm, EditarVendasForm
from .models import Venda, ArquivoVendedor, Produto, CustomUser, MetaAcrescimo
from .utils import calcular_total_comissao, calcular_meta_restante, calcular_meta_vendedor


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
 # Exibindo todos os erros de validação
            print("Formulário inválido:")
            for field, errors in form.errors.items():
                print(f"Erro no campo {field}: {errors}")
            messages.error(request, 'Usuário ou senha inválidos.')

    else:
        form = AuthenticationForm()

    return render(request, 'index.html', {'form': form})

@login_required
def home_vendedor(request):
    return render(request, 'home_vendedor.html')

@login_required
def home_adm(request):
    # Pega mês e ano do filtro ou usa o mês/ano atual
    mes = int(request.GET.get('mes', datetime.datetime.now().month))
    ano = int(request.GET.get('ano', datetime.datetime.now().year))

    # Filtra as vendas pelo mês e ano
    vendas = Venda.objects.filter(data_venda__year=ano, data_venda__month=mes)
    vendas_ano = Venda.objects.filter(data_venda__year=ano)
    
    # Dicionário para armazenar vendas por mês
    vendas_por_mes = defaultdict(int)
    
    # Somar as quantidades vendidas por mês
    for venda_ano in vendas_ano:
        mes_venda = venda_ano.data_venda.month 
        vendas_por_mes[mes_venda] += venda_ano.quantidade_vendida
        
     # Criar lista ordenada para o gráfico
    vendas_mensais = [vendas_por_mes.get(m, 0) for m in range(1, 13)]

    # Dicionário para armazenar vendas por vendedor
    vendas_por_vendedor = {}

    # Organizar vendas por vendedor
    for venda in vendas:
        vendedor_id = venda.vendedor.id

        if vendedor_id not in vendas_por_vendedor:
            vendas_por_vendedor[vendedor_id] = []

        vendas_por_vendedor[vendedor_id].append(venda)

    # Aplicação do cálculo de comissão por vendedor
    for vendedor_id, vendas_vendedor in vendas_por_vendedor.items():
        total_pecas, total_valor = calcular_total_comissao(vendas_vendedor)
        vendas_por_vendedor[vendedor_id] = {
            'total_geral_pecas': total_pecas,
            'total_geral_valor': total_valor,
        }

    # Soma a comissão total dos vendedores
    total_comissao = sum(dados['total_geral_valor'] for dados in vendas_por_vendedor.values())

    # Calcula o total de peças vendidas
    total_pecas = sum(dados['total_geral_pecas'] for dados in vendas_por_vendedor.values())

    # Meta
    meta_maxima = MetaAcrescimo.objects.aggregate(max_valor=Max("min_pecas"))["max_valor"] or 1000

    user = get_user_model()  # Pega o modelo de usuário correto
    num_vendedores = user.objects.filter(is_staff=False).count()
    meta_total_mes = meta_maxima * num_vendedores

    porcentagem_meta = (total_pecas / meta_total_mes) * 100 if meta_total_mes > 0 else 0

    # Ranking de produtos (ordenado pelo total vendido)
    ranking_produtos = vendas.values('produto__nome').annotate(
        total_vendido=Sum('quantidade_vendida')
    ).order_by('-total_vendido')
    
    # Ranking de vendedores (ordenado pelo total vendido)
    ranking_vendedores = calcular_meta_restante(request)  # Passa a requisição aqui

    # Lista de meses para o filtro
    meses_disponiveis = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
        (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
        (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
    ]
    
    # Obtém todos os anos disponíveis no banco de dados ordenados do mais recente ao mais antigo
    anos_disponiveis = (
        Venda.objects.values_list("data_venda__year", flat=True)
        .distinct()
        .order_by("-data_venda__year")
    )

    context = {
        'total_pecas': total_pecas,
        'total_comissao': total_comissao,  
        'ranking_produtos': ranking_produtos,
        'ranking_vendedores': ranking_vendedores,  
        'mes': mes,
        'ano': ano,
        'meses_disponiveis': meses_disponiveis,
        'anos_disponiveis': anos_disponiveis,
        'porcentagem_meta': porcentagem_meta,
        'mes_atual': datetime.datetime.now().month,
        'ano_atual': datetime.datetime.now().year,
        'vendas_mensais': vendas_mensais,  
    }

    return render(request, 'home_adm.html', context)


@login_required
def registrar_venda(request):
    if request.method == "POST":
        form = VendaForm(request.POST, user=request.user)  # 🔹 Passa o usuário para filtrar as lojas
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
        form = VendaForm(user=request.user)  # 🔹 Passa o usuário também na criação inicial

    vendas = Venda.objects.filter(vendedor=request.user).order_by('-data_venda')

    return render(request, "registrar_venda.html", {"form": form, "vendas": vendas})


# Verifica se o usuário é administrador
def is_admin(user):
    return user.is_staff  # Apenas administradores terão acesso


@login_required
def relatorio_vendas(request):
    # Pega mês e ano do filtro ou usa o mês/ano atual
    mes = int(request.GET.get('mes', datetime.datetime.now().month))
    ano = int(request.GET.get('ano', datetime.datetime.now().year))
    
    vendas = Venda.objects.filter(data_venda__year=ano, data_venda__month=mes)
    produtos = Produto.objects.all()

    # Obtém a meta máxima definida no sistema
    meta_maxima = MetaAcrescimo.objects.aggregate(max_valor=Max("min_pecas"))["max_valor"] or 1000

    # Agrupamento por vendedor
    vendas_por_vendedor = {}

    for venda in vendas:
        vendedor_id = venda.vendedor.id

        # Inicializa os dados do vendedor
        if vendedor_id not in vendas_por_vendedor:
            vendas_por_vendedor[vendedor_id] = {
                'vendedor': venda.vendedor,
                'total_por_produto': {produto.id: 0 for produto in produtos},
                'valor_por_produto': {produto.id: 0 for produto in produtos},
            }

        # Atualiza os totais por vendedor
        vendas_por_vendedor[vendedor_id]['total_por_produto'][venda.produto.id] += venda.quantidade_vendida

    # Aplicação do cálculo de comissão baseado no total de peças vendidas
    for vendedor_id, dados in vendas_por_vendedor.items():
        vendas_vendedor = vendas.filter(vendedor__id=vendedor_id)
        total_pecas, total_valor = calcular_total_comissao(vendas_vendedor)

        # Calcula a meta restante e o percentual atingido
        meta_restante = max(meta_maxima - total_pecas, 0)
        percentual_meta = (total_pecas / meta_maxima) * 100 if meta_maxima > 0 else 0

        dados['total_geral_pecas'] = total_pecas
        dados['total_geral_valor'] = total_valor
        dados['meta_restante'] = meta_restante
        dados['percentual_meta'] = percentual_meta

    # Ordenando as vendas por quantidade (mais vendido no topo)
    vendas_por_vendedor = dict(sorted(vendas_por_vendedor.items(), key=lambda item: item[1]['total_geral_pecas'], reverse=True))
    
        # Lista de meses para o filtro
    meses_disponiveis = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
        (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
        (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
    ]
    
    # Obtém todos os anos disponíveis no banco de dados ordenados do mais recente ao mais antigo
    anos_disponiveis = (
        Venda.objects.values_list("data_venda__year", flat=True)
        .distinct()
        .order_by("-data_venda__year")
    )

    return render(request, "relatorio_vendas.html", {
        "vendas_por_vendedor": vendas_por_vendedor,
        "meta_maxima": meta_maxima,
        "ano": ano,
        "mes": mes,
        'meses_disponiveis': meses_disponiveis,
        'anos_disponiveis': anos_disponiveis,
    })


@login_required
def logout_view(request):
    logout(request)
    return redirect('index.html')

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

def obter_acrescimo(total_pecas):
    """ Busca no banco o acréscimo correto para o número total de peças vendidas """
    metas = MetaAcrescimo.objects.order_by("min_pecas")  # Garante a ordem correta
    for meta in metas:
        if meta.max_pecas is None or (meta.min_pecas <= total_pecas <= meta.max_pecas):
            return meta.acrescimo
    return 0  # Se não houver correspondência, não há acréscimo


@login_required
def selos(request, id_vendedor=None):
    if id_vendedor:
        if not request.user.is_staff:
            return redirect("home_vendedor")
        vendedor = get_object_or_404(CustomUser, id=id_vendedor)
    else:
        vendedor = request.user

    today = datetime.date.today()
    mes_atual = today.month
    ano_atual = today.year

    ano = int(request.GET.get("ano", ano_atual))
    mes = int(request.GET.get("mes", mes_atual))
    dia = request.GET.get("dia")  # Dia pode ser opcional

    vendas = Venda.objects.filter(vendedor=vendedor, data_venda__year=ano, data_venda__month=mes)

    if dia:
        vendas = vendas.filter(data_venda__day=int(dia))

    produtos = Produto.objects.all()

    if dia:
        vendas_por_dia = {int(dia): {produto.id: 0 for produto in produtos}}
    else:
        vendas_por_dia = {d: {produto.id: 0 for produto in produtos} for d in range(1, calendar.monthrange(ano, mes)[1] + 1)}

    for venda in vendas:
        vendas_por_dia[venda.data_venda.day][venda.produto.id] = venda.quantidade_vendida

    # 🔹 Mantemos total_por_produto para ser usado no template
    total_por_produto = {produto.id: 0 for produto in produtos}

    for venda in vendas:
        total_por_produto[venda.produto.id] += venda.quantidade_vendida

    # 🔹 Calculamos comissão e obtemos valores atualizados
    total_geral_pecas, total_geral_valor = calcular_total_comissao(vendas)

    # 🔹 Precisamos recuperar os valores por produto para exibir no template
    valor_por_produto = {produto.id: total_por_produto[produto.id] * produto.valor for produto in produtos}

    DIAS_SEMANA = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }

    if dia:
        dias_formatados = {
            int(dia): DIAS_SEMANA.get(datetime.date(ano, mes, int(dia)).strftime("%A"), "Desconhecido")
        }
    else:
        dias_formatados = {
            d: DIAS_SEMANA.get(datetime.date(ano, mes, d).strftime("%A"), "Desconhecido")
            for d in vendas_por_dia.keys()
        }
        
    # Calculando a porcentagem de vendas em relação à meta
    meta_maxima = MetaAcrescimo.objects.aggregate(max_valor=Max("min_pecas"))["max_valor"] or 1000
    porcentagem_vendas = round((total_geral_pecas / meta_maxima) * 100, 2) if meta_maxima else 0

    porcentagem_vendas = str(porcentagem_vendas).replace(',', '.')
    
    meta_restante = calcular_meta_vendedor(vendedor)

    return render(
        request,
        "selos.html",
        {
            "ano_atual": ano_atual,
            "mes_atual": mes_atual,
            "anos_disponiveis": list(range(ano_atual, 2031)),
            "meses_disponiveis": range(1, 13),
            "vendas_por_dia": vendas_por_dia,
            "produtos": produtos,
            "total_por_produto": total_por_produto,  # ✅ Restaurado para evitar erro no template
            "valor_por_produto": valor_por_produto,  # ✅ Restaurado para evitar erro no template
            "total_geral_pecas": total_geral_pecas,
            "total_geral_valor": total_geral_valor,
            "dias_formatados": dias_formatados,
            "ano": ano,
            "mes": mes,
            "vendedor": vendedor,
            "porcentagem_vendas": porcentagem_vendas,  
            "meta_restante": meta_restante,
        },
    )

    
@login_required
def editar_vendas(request, data):
    # Converte a data para o formato de data
    data_venda = datetime.datetime.strptime(data, "%Y-%m-%d").date()

    # Se for admin, pode editar todas as vendas desse dia. Senão, edita apenas as suas.
    if request.user.is_superuser:
        vendas = Venda.objects.filter(data_venda=data_venda)
    else:
        vendas = Venda.objects.filter(data_venda=data_venda, vendedor=request.user)

    if not vendas.exists():
        return redirect('registrar_venda')

    # Criação do formulário
    if request.method == "POST":
        for venda in vendas:
            quantidade = request.POST.get(f'quantidade_vendida_{venda.id}')
            if quantidade:
                venda.quantidade_vendida = int(quantidade)
                venda.save()

            # Verifica se o usuário quer excluir o produto
            excluir_produto = request.POST.get(f'excluir_{venda.id}')
            if excluir_produto == 'on':  # Se o checkbox de excluir foi marcado
                venda.delete()
                messages.success(request, f"Produto {venda.produto.nome} excluído com sucesso!")

        messages.success(request, "Vendas atualizadas com sucesso!")
        return redirect('selos')
    else:
        # Caso não seja POST, cria o formulário com os dados existentes
        form = EditarVendasForm()

    # Passa as vendas do dia para o template
    return render(request, 'editar_vendas.html', {
        'form': form, 
        'data': data,
        'vendas': vendas,  # Passa as vendas para o template
        'data_venda' : data_venda
    })


@login_required
def apagar_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id, vendedor=request.user)

    if request.method == "POST":
        venda.delete()
        messages.success(request, "Venda excluída com sucesso!")
        return redirect('selos')

    return render(request, 'confirmar_exclusao.html', {'venda': venda})

class CustomPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset_form.html"
    success_url = reverse_lazy("password_reset_done")
    
def error_404_view(request, exception):
    return render(request, '404.html', status=404)