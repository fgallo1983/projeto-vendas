import datetime
from django.db.models import Min,Sum, Max, Value
from django.contrib.auth import get_user_model
from django.db.models.functions import Concat
from .models import Venda, Produto, MetaAcrescimo, CustomUser, MetaVendedora


def obter_acrescimo(total_pecas, vendedor=None):
    """
    Retorna o acréscimo com base no total de peças vendidas.
    Prioriza metas específicas da vendedora, se existirem.
    """
    faixas = None

    if vendedor:
        faixas = MetaVendedora.objects.filter(vendedora=vendedor).order_by("min_pecas")
        if not faixas.exists():
            # Se não houver faixas específicas, usa as padrão
            faixas = MetaAcrescimo.objects.all().order_by("min_pecas")
    else:
        faixas = MetaAcrescimo.objects.all().order_by("min_pecas")

    for faixa in faixas:
        if faixa.min_pecas <= total_pecas <= (faixa.max_pecas or total_pecas):
            return faixa.acrescimo

    return 0  # Se não houver nenhuma faixa correspondente, retorna 0

from django.db.models import Min

def calcular_total_comissao(vendas, vendedor=None):
    """Calcula o valor total da comissão das vendas fornecidas."""
    produtos = Produto.objects.all()

    total_por_produto = {produto.id: 0 for produto in produtos}
    valor_por_produto = {produto.id: 0 for produto in produtos}

    for venda in vendas:
        total_por_produto[venda.produto.id] += venda.quantidade_vendida

    total_geral_pecas = sum(total_por_produto.values())
    acrescimo = obter_acrescimo(total_geral_pecas, vendedor)

    # 🔹 Busca meta mínima com prioridade para a vendedora
    if vendedor:
        meta_vendedora = MetaVendedora.objects.filter(vendedora=vendedor).aggregate(
            min_valor=Min("min_pecas")
        )["min_valor"]
    else:
        meta_vendedora = None

    meta_minima = meta_vendedora if meta_vendedora is not None else MetaAcrescimo.objects.aggregate(
        min_valor=Min("min_pecas")
    )["min_valor"] or 0

    for produto in produtos:
        preco_base = produto.valor or 0
        preco_final = preco_base

        if total_geral_pecas >= meta_minima and preco_base <= 1.00 and produto.id != 7:
            preco_final = preco_base + acrescimo

        valor_por_produto[produto.id] = total_por_produto[produto.id] * preco_final

    total_geral_valor = sum(valor_por_produto.values())
    return total_geral_pecas, total_geral_valor

def calcular_meta_restante(request):
    """Calcula a meta restante para as top 3 vendedoras, considerando metas específicas"""

    mes = int(request.GET.get('mes', datetime.datetime.now().month))
    ano = int(request.GET.get('ano', datetime.datetime.now().year))

    ranking_vendedores = Venda.objects.filter(
        data_venda__year=ano,
        data_venda__month=mes
    ).annotate(
        vendedor_nome=Concat('vendedor__first_name', Value(' '), 'vendedor__last_name')
    ).values('vendedor_nome', 'vendedor_id').annotate(
        total_vendido=Sum('quantidade_vendida')
    ).order_by('-total_vendido')[:3]

    for vendedor in ranking_vendedores:
        total_vendido = vendedor["total_vendido"]
        vendedor_id = vendedor["vendedor_id"]

        # Tenta usar metas específicas
        faixas = MetaVendedora.objects.filter(vendedora_id=vendedor_id).order_by("min_pecas")
        if not faixas.exists():
            faixas = MetaAcrescimo.objects.order_by("min_pecas")

        meta_restante = 0
        for faixa in faixas:
            if total_vendido < faixa.min_pecas:
                meta_restante = faixa.min_pecas - total_vendido
                break
            elif faixa.max_pecas and total_vendido <= faixa.max_pecas:
                meta_restante = (faixa.max_pecas + 1) - total_vendido
                break

        vendedor["meta_restante"] = meta_restante

    return ranking_vendedores

def calcular_meta_vendedor(vendedor, mes, ano):
    """Calcula a quantidade restante para a próxima meta da vendedora (ou padrão)"""

    # Total de peças vendidas no mês/ano atual
    total_vendido = Venda.objects.filter(
        vendedor=vendedor,
        data_venda__year=ano,
        data_venda__month=mes
    ).aggregate(total=Sum('quantidade_vendida'))["total"] or 0

    # Tenta buscar metas específicas para a vendedora
    faixas = MetaVendedora.objects.filter(vendedora=vendedor).order_by("min_pecas")
    if not faixas.exists():
        faixas = MetaAcrescimo.objects.order_by("min_pecas")

    for faixa in faixas:
        if total_vendido < faixa.min_pecas:
            return faixa.min_pecas - total_vendido
        elif faixa.max_pecas and total_vendido <= faixa.max_pecas:
            return (faixa.max_pecas + 1) - total_vendido

    return 0  # Já atingiu todas as metas

def obter_faixa_atual(total_pecas, vendedor=None):

    if vendedor:
        faixas = MetaVendedora.objects.filter(vendedora=vendedor).order_by("min_pecas")
        if not faixas.exists():
            faixas = MetaAcrescimo.objects.all().order_by("min_pecas")
    else:
        faixas = MetaAcrescimo.objects.all().order_by("min_pecas")

    for faixa in faixas:
        if faixa.max_pecas:
            if faixa.min_pecas <= total_pecas <= faixa.max_pecas:
                return faixa
        else:
            if total_pecas >= faixa.min_pecas:
                return faixa

    return None  # Ainda não atingiu nenhuma faixa


def obter_proxima_meta(total_pecas, vendedor=None):
    """
    Retorna o valor (min_pecas) da próxima meta a ser atingida.
    Considera metas específicas da vendedora se existirem.
    """
    if vendedor:
        faixas = MetaVendedora.objects.filter(vendedora=vendedor).order_by("min_pecas")
        if not faixas.exists():
            faixas = MetaAcrescimo.objects.all().order_by("min_pecas")
    else:
        faixas = MetaAcrescimo.objects.all().order_by("min_pecas")

    for faixa in faixas:
        if total_pecas < faixa.min_pecas:
            return faixa.min_pecas
        elif faixa.max_pecas and total_pecas <= faixa.max_pecas:
            return faixa.max_pecas + 1

    return None  # Já atingiu a última faixa

def obter_acrescimo_por_vendedora(vendedora, total_pecas):
    # Primeiro, tenta achar faixas personalizadas
    faixas = MetaVendedora.objects.filter(vendedora=vendedora).order_by('min_pecas')

    if not faixas.exists():
        # Se não houver faixas personalizadas, usa o padrão
        faixas = MetaAcrescimo.objects.all()

    for faixa in faixas:
        if faixa.max_pecas is None:
            if total_pecas >= faixa.min_pecas:
                return faixa.acrescimo
        elif faixa.min_pecas <= total_pecas <= faixa.max_pecas:
            return faixa.acrescimo

    return 0.0  # Nenhuma faixa aplicável
