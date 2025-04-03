import datetime
from django.db.models import Min,Sum, Max, Value
from django.contrib.auth import get_user_model
from django.db.models.functions import Concat
from .models import Venda, Produto, MetaAcrescimo, CustomUser


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
    """Calcula a meta restante para cada vendedora"""
    
    # Obtém o valor máximo da meta
    meta_maxima = MetaAcrescimo.objects.aggregate(max_valor=Max("min_pecas"))["max_valor"] or 1000

    # Obtém o mês e ano filtrados ou usa os valores padrão
    mes = int(request.GET.get('mes', datetime.datetime.now().month))
    ano = int(request.GET.get('ano', datetime.datetime.now().year))

    # Filtra as vendas de acordo com o mês e ano selecionados
    ranking_vendedores = Venda.objects.filter(
        data_venda__year=ano,  # Filtra pelo ano
        data_venda__month=mes  # Filtra pelo mês
    ).annotate(
        vendedor_nome=Concat('vendedor__first_name', Value(' '), 'vendedor__last_name')
    ).values('vendedor_nome').annotate(
        total_vendido=Sum('quantidade_vendida')
    ).order_by('-total_vendido')[:3]  # Pegamos apenas os 3 melhores
    # Adicionamos a meta restante para cada vendedora
    for vendedor in ranking_vendedores:
        vendedor["meta_restante"] = max((meta_maxima-1) - vendedor["total_vendido"], 0)

    return ranking_vendedores

def calcular_meta_vendedor(vendedor):
    """Calcula a meta restante para uma vendedora específica"""
    
    # Obtém o valor máximo da meta
    meta_maxima = MetaAcrescimo.objects.aggregate(max_valor=Max("min_pecas"))["max_valor"] or 1000

    # Obtém as vendas da vendedora específica
    total_vendido = Venda.objects.filter(vendedor=vendedor).aggregate(
        total_vendido=Sum('quantidade_vendida')
    )["total_vendido"] or 0  # Se não houver vendas, retorna 0
    
    # Calcula a meta restante
    meta_restante = max((meta_maxima-1) - total_vendido, 0)

    return meta_restante