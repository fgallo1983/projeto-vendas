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
from django.utils.http import urlencode
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from .forms import VendaForm, RoteiroForm, EditarVendasForm
from .utils import calcular_total_comissao, calcular_meta_restante, calcular_meta_vendedor, obter_faixa_atual, obter_proxima_meta
from django.contrib.auth.views import PasswordResetView 
from .models import Venda, ArquivoVendedor, Produto, CustomUser, MetaAcrescimo, Loja

User = get_user_model()

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
    
    # Pega mês e ano do filtro ou usa o mês/ano atual
    mes = int(request.GET.get('mes', datetime.datetime.now().month))
    ano = int(request.GET.get('ano', datetime.datetime.now().year))
    
    vendedor = request.user

    vendas = Venda.objects.filter(vendedor=vendedor, data_venda__year=ano, data_venda__month=mes)
    vendas_ano = Venda.objects.filter(vendedor=vendedor, data_venda__year=ano)
    
    # Dicionário para armazenar vendas por mês
    vendas_por_mes = defaultdict(int)
    
    # Somar as quantidades vendidas por mês
    for venda_ano in vendas_ano:
        mes_venda = venda_ano.data_venda.month
        vendas_por_mes[mes_venda] += venda_ano.quantidade_vendida
        
     # Criar lista ordenada para o gráfico
    vendas_mensais = [vendas_por_mes.get(m, 0) for m in range(1, 13)]
    print (vendas_mensais)
    
    produtos = Produto.objects.all()

    vendas_por_dia = {d: {produto.id: 0 for produto in produtos} for d in range(1, calendar.monthrange(ano, mes)[1] + 1)}

    for venda in vendas:
        vendas_por_dia[venda.data_venda.day][venda.produto.id] = venda.quantidade_vendida

    # 🔹 Mantemos total_por_produto para ser usado no template
    total_por_produto = {produto.id: 0 for produto in produtos}

    for venda in vendas:
        total_por_produto[venda.produto.id] += venda.quantidade_vendida

    # 🔹 Calculamos comissão e obtemos valores atualizados
    total_geral_pecas, total_geral_valor = calcular_total_comissao(vendas)
    
        # 🔹 Faixa atual de meta
    faixa_atual = obter_faixa_atual(total_geral_pecas)

    # 🔹 Próxima meta
    proxima_meta = obter_proxima_meta(total_geral_pecas)
    
    meta_restante = calcular_meta_vendedor(vendedor, mes, ano)
    
    # Supondo que todos os produtos tenham o mesmo valor base de comissão
    preco_base = Produto.objects.first().valor if Produto.objects.exists() else 0
    
    # Se houver faixa atual, calcula o valor da comissão por peça
    comissao_atual = preco_base + faixa_atual.acrescimo if faixa_atual else 0
    
    # Filtra as vendas de acordo com o mês e ano selecionados
    ranking_vendedores = Venda.objects.filter(
        data_venda__year=ano,  # Filtra pelo ano
        data_venda__month=mes  # Filtra pelo mês
    ).annotate(
        vendedor_nome=Concat('vendedor__first_name', Value(' '), 'vendedor__last_name')
    ).values('vendedor_nome').annotate(
        total_vendido=Sum('quantidade_vendida')
    ).order_by('-total_vendido')[:6]  # Pegamos apenas os 3 melhores
    
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
    
    if not anos_disponiveis:
        anos_disponiveis = [ano]
    
    context = {
        'total_geral_pecas': total_geral_pecas,
        'total_geral_valor': total_geral_valor,  
        'mes': mes,
        'ano': ano,
        'meses_disponiveis': meses_disponiveis,
        'anos_disponiveis': anos_disponiveis,
        'meta_restante': meta_restante,
        'ranking_vendedores': ranking_vendedores,
        'vendas_mensais': vendas_mensais, 
        'faixa_atual': faixa_atual,
        'proxima_meta': proxima_meta,
        'preco_base': preco_base,
        'comissao_atual': comissao_atual,
    }

    return render(request, 'home_vendedor.html', context)

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
    
    if not anos_disponiveis:
        anos_disponiveis = [ano]

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
    id_vendedora = request.GET.get("id_vendedora")
    data_inicial = request.GET.get("data")  # Para preencher o campo data_venda

    vendedor = None

    if request.user.is_staff:
        if id_vendedora:
            vendedor = get_object_or_404(CustomUser, id=id_vendedora, is_staff=False)
    else:
        vendedor = request.user

    if request.method == "POST":
        form = VendaForm(request.POST, user=request.user)

        if form.is_valid():
            # Campos únicos fora do loop
            data_venda = form.cleaned_data['data_venda']
            loja = form.cleaned_data['loja']

            if request.user.is_staff:
                vendedor = form.cleaned_data.get('vendedor')
                if not vendedor:
                    messages.error(request, "Selecione uma vendedora.")
                    return render(request, "registrar_venda.html", {"form": form})
            else:
                vendedor = request.user

            # Recebe listas de produtos e quantidades
            produtos = request.POST.getlist('produto')
            quantidades = request.POST.getlist('quantidade_vendida')

            vendas_registradas = 0
            erros = []

            for produto_id, quantidade_str in zip(produtos, quantidades):
                if not produto_id or not quantidade_str:
                    continue  # Pula campos vazios

                try:
                    produto = Produto.objects.get(id=produto_id)
                    quantidade = int(quantidade_str)
                except (Produto.DoesNotExist, ValueError):
                    erros.append("Produto inválido ou quantidade inválida.")
                    continue

                # Verifica se já existe venda desse produto na mesma data e loja
                venda_existente = Venda.objects.filter(
                    produto=produto,
                    data_venda=data_venda,
                    vendedor=vendedor,
                    loja=loja  
                ).exists()

                if venda_existente:
                    erros.append(f"O produto '{produto.nome}' já foi registrado nesse dia nesta loja. Use o editar vendas no relatório.")
                    continue

                # Cria e salva a venda
                venda = Venda(
                    produto=produto,
                    quantidade_vendida=quantidade,
                    data_venda=data_venda,
                    loja=loja,
                    vendedor=vendedor,
                    valor=quantidade * produto.valor
                )
                venda.save()
                vendas_registradas += 1

            if vendas_registradas > 0:
                messages.success(request, f"{vendas_registradas} venda(s) registrada(s) com sucesso!")
                request.session['dia_destacado'] = data_venda.day
                redirect_url = (
                    reverse('selos', kwargs={'id_vendedor': vendedor.id})
                    if request.user.is_staff else reverse('selos')
                )
                return redirect(f"{redirect_url}?ano={data_venda.year}&mes={data_venda.month}")
            else:
                for erro in erros:
                    messages.error(request, erro)

    else:
        initial_data = {}
        if data_inicial:
            initial_data['data_venda'] = data_inicial
        if vendedor:
            initial_data['vendedor'] = vendedor

        form = VendaForm(user=request.user, vendedor=vendedor, initial=initial_data)

    return render(request, "registrar_venda.html", {"form": form})
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
        percentual_meta = (total_pecas / (meta_maxima-1)) * 100 if meta_maxima > 0 else 0

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
    if not anos_disponiveis:
        anos_disponiveis = [ano]

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

def obter_acrescimo(total_pecas):
    """ Busca no banco o acréscimo correto para o número total de peças vendidas """
    metas = MetaAcrescimo.objects.order_by("min_pecas")  # Garante a ordem correta
    for meta in metas:
        if meta.max_pecas is None or (meta.min_pecas <= total_pecas <= meta.max_pecas):
            return meta.acrescimo
    return 0  # Se não houver correspondência, não há acréscimo


@login_required
def selos(request, id_vendedor=None):
    request.session["id_vendedor"] = id_vendedor
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
    dia = request.GET.get("dia")
    dia_destacado = request.session.pop('dia_destacado', None)

    # 🔸 Vendas do mês inteiro (para indicadores)
    vendas_mes = Venda.objects.filter(vendedor=vendedor, data_venda__year=ano, data_venda__month=mes)

    # 🔸 Vendas filtradas por dia (para a tabela)
    vendas_tabela = vendas_mes
    if dia:
        vendas_tabela = vendas_mes.filter(data_venda__day=int(dia))

    produtos = Produto.objects.all()

    if dia:
        vendas_por_dia = {int(dia): {produto.id: 0 for produto in produtos}}
    else:
        vendas_por_dia = {d: {produto.id: 0 for produto in produtos} for d in range(1, calendar.monthrange(ano, mes)[1] + 1)}

    for venda in vendas_tabela:
        vendas_por_dia[venda.data_venda.day][venda.produto.id] += venda.quantidade_vendida

    total_por_produto = {produto.id: 0 for produto in produtos}
    for venda in vendas_tabela:
        total_por_produto[venda.produto.id] += venda.quantidade_vendida

    # 🔹 Cálculo dos totais com base nas vendas do mês
    total_geral_pecas, total_geral_valor = calcular_total_comissao(vendas_mes)

    valor_por_produto = {}
    acrescimo = obter_acrescimo(total_geral_pecas)
    meta_minima = MetaAcrescimo.objects.aggregate(min_valor=Min("min_pecas"))["min_valor"] or 0

    for produto in produtos:
        preco_base = produto.valor or 0
        if total_geral_pecas < meta_minima:
            preco_final = preco_base
        else:
            preco_final = preco_base + acrescimo if preco_base <= 1.00 and produto.id != 7 else preco_base

        valor_por_produto[produto.id] = total_por_produto[produto.id] * preco_final

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

    meta_restante = calcular_meta_vendedor(vendedor, mes, ano)
    faixa_atual = obter_faixa_atual(total_geral_pecas)
    proxima_meta = obter_proxima_meta(total_geral_pecas)

    preco_base = Produto.objects.first().valor if Produto.objects.exists() else 0
    comissao_atual = preco_base + faixa_atual.acrescimo if faixa_atual else 0

    porcentagem_vendas = round((total_geral_pecas / proxima_meta) * 100, 2) if proxima_meta else 0
    porcentagem_vendas = str(porcentagem_vendas).replace(',', '.')

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
            "total_por_produto": total_por_produto,
            "valor_por_produto": valor_por_produto,
            "total_geral_pecas": total_geral_pecas,
            "total_geral_valor": total_geral_valor,
            "dias_formatados": dias_formatados,
            "ano": ano,
            "mes": mes,
            "vendedor": vendedor,
            "porcentagem_vendas": porcentagem_vendas,
            "meta_restante": meta_restante,
            "dia_destacado": dia_destacado,
            "faixa_atual": faixa_atual,
            "proxima_meta": proxima_meta,
            "preco_base": preco_base,
            "comissao_atual": comissao_atual,
        },
    )

    
@login_required
def editar_vendas(request, id_vendedor, data):
    data_venda = datetime.datetime.strptime(data, "%Y-%m-%d").date()

    if request.user.is_superuser:
        vendedor = get_object_or_404(User, id=id_vendedor)
    else:
        vendedor = request.user

    vendas = Venda.objects.filter(data_venda=data_venda, vendedor=vendedor)

    if not vendas.exists():
        url = reverse('registrar_venda')
        query_string = urlencode({
            'id_vendedora': id_vendedor or request.user.id,
            'data': data  # <-- aqui vai a data formatada
        })
        full_url = f'{url}?{query_string}'
        return redirect(full_url)

    if request.method == "POST":
        for venda in vendas:
            quantidade = request.POST.get(f'quantidade_vendida_{venda.id}')
            if quantidade is not None:
                venda.quantidade_vendida = int(quantidade)
                venda.save()

            if request.POST.get(f'excluir_{venda.id}') == 'on':
                venda.delete()

        messages.success(request, "Vendas atualizadas com sucesso!")
        # dia = data_venda.day
        request.session['dia_destacado'] = data_venda.day  # ← AQUI

        if request.user.is_superuser:
            return redirect(f"{reverse('selos', kwargs={'id_vendedor': id_vendedor})}")
        else:
            return redirect(f"{reverse('selos')}")

    return render(request, 'editar_vendas.html', {
        'form': EditarVendasForm(),
        'data': data,
        'vendas': vendas,
        'data_venda': data_venda,
        'vendedor': vendedor
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

@login_required
def carregar_lojas_por_vendedora(request):
    id_vendedora = request.GET.get('id_vendedora')
    try:
        vendedora = CustomUser.objects.get(id=id_vendedora, is_staff=False)
        lojas = vendedora.lojas.all().values('id', 'nome', 'cidade')
        return JsonResponse(list(lojas), safe=False)
    except CustomUser.DoesNotExist:
        return JsonResponse([], safe=False)