import datetime
from django.db.models import Min,Sum, Max, Value
from django.contrib.auth import get_user_model
from django.db.models.functions import Concat
from .models import Venda, Produto, MetaAcrescimo, CustomUser


META_MINIMA_FIXA = 401  # Aqui fixamos a meta inicial, ignorando faixas abaixo

def obter_acrescimo(total_pecas):
    """Retorna o acréscimo com base no total de peças vendidas."""
    faixas_acrescimo = MetaAcrescimo.objects.all()
    for faixa in faixas_acrescimo:
        if faixa.min_pecas <= total_pecas <= (faixa.max_pecas or total_pecas):
            return faixa.acrescimo
    return 0  # Retorna 0 caso não se encaixe em nenhuma faixa

def calcular_total_comissao(vendas):
    """Calcula o valor total da comissão das vendas fornecidas."""
    produtos = Produto.objects.all()

    total_por_produto = {produto.id: 0 for produto in produtos}
    valor_por_produto = {produto.id: 0 for produto in produtos}

    for venda in vendas:
        total_por_produto[venda.produto.id] += venda.quantidade_vendida

    total_geral_pecas = sum(total_por_produto.values())

    # 🔹 Busca o acréscimo correto no banco de dados
    acrescimo = obter_acrescimo(total_geral_pecas)

    # Obtém a menor meta cadastrada no banco
    meta_minima = MetaAcrescimo.objects.aggregate(min_valor=Min("min_pecas"))["min_valor"] or 0

    # Ajusta os valores dos produtos sem alterar o banco de dados
    for produto in produtos:
        preco_base = produto.valor or 0

        # Se ainda não atingiu a meta mínima, mantém o preço base
        if total_geral_pecas < meta_minima:
            preco_final = preco_base
        else:
            # Apenas produtos com preço base <= 1.00 recebem acréscimo
            preco_final = preco_base + acrescimo if preco_base <= 1.00 else preco_base
        
        # Calcula o valor total por produto
        valor_por_produto[produto.id] = total_por_produto[produto.id] * preco_final

    total_geral_valor = sum(valor_por_produto.values())

    return total_geral_pecas, total_geral_valor

def calcular_meta_restante(request):
    """Calcula a meta restante para as top vendedoras, ignorando a primeira faixa"""

    mes = int(request.GET.get('mes', datetime.datetime.now().month))
    ano = int(request.GET.get('ano', datetime.datetime.now().year))

    metas = list(MetaAcrescimo.objects.order_by('min_pecas'))[1:]  # Ignora a primeira linha

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

        meta_restante = 0
        for meta in metas:
            if total_vendido < meta.min_pecas:
                meta_restante = meta.min_pecas - total_vendido
                break

        vendedor["meta_restante"] = meta_restante

    return ranking_vendedores

def calcular_meta_vendedor(vendedor, mes, ano):
    """Calcula a quantidade restante para a próxima meta, ignorando a primeira faixa"""

    total_vendido = Venda.objects.filter(
        vendedor=vendedor, 
        data_venda__year=ano, 
        data_venda__month=mes
    ).aggregate(total=Sum('quantidade_vendida'))["total"] or 0

    # Pega as faixas a partir da segunda (ignora a primeira)
    metas = list(MetaAcrescimo.objects.order_by('min_pecas'))[1:]

    for meta in metas:
        if total_vendido < meta.min_pecas:
            return meta.min_pecas - total_vendido

    return 0  # Já bateu todas as metas relevantes

def obter_faixa_atual(total_pecas):
    """
    Retorna a faixa de acréscimo correspondente à quantidade total de peças, ignorando faixas abaixo da meta mínima.
    """
    faixas = MetaAcrescimo.objects.filter(min_pecas__gte=META_MINIMA_FIXA).order_by("min_pecas")

    for faixa in faixas:
        if faixa.max_pecas:
            if faixa.min_pecas <= total_pecas <= faixa.max_pecas:
                return faixa
        else:
            if total_pecas >= faixa.min_pecas:
                return faixa
    return None  # Ainda não atingiu a faixa inicial


def obter_proxima_meta(total_pecas):
    """
    Retorna o valor (min_pecas) da próxima meta a ser atingida, considerando que a meta começa em 401.
    """
    faixas = MetaAcrescimo.objects.filter(min_pecas__gte=META_MINIMA_FIXA).order_by("min_pecas")

    for faixa in faixas:
        if total_pecas < faixa.min_pecas:
            return faixa.min_pecas
        elif faixa.max_pecas and total_pecas <= faixa.max_pecas:
            return faixa.max_pecas + 1

    return None  # Já bateu a última faixa
