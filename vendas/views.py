from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import VendaForm, RoteiroForm, EditarVendasForm
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
from datetime import date
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy


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
    return render(request, 'home_adm.html')


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
    today = datetime.date.today()
    mes_atual = today.month
    ano_atual = today.year

    ano = int(request.GET.get('ano', ano_atual))
    mes = int(request.GET.get('mes', mes_atual))

    vendas = Venda.objects.filter(data_venda__year=ano, data_venda__month=mes)
    produtos = Produto.objects.all()

    # Agrupamento por vendedor
    vendas_por_vendedor = {}
    vendas_por_loja = {}

    for venda in vendas:
        vendedor_id = venda.vendedor.id
        loja_id = venda.loja.id  # Pega a loja diretamente da venda

        # Inicializa os dados do vendedor
        if vendedor_id not in vendas_por_vendedor:
            vendas_por_vendedor[vendedor_id] = {
                'vendedor': venda.vendedor,
                'total_por_produto': {produto.id: 0 for produto in produtos},
                'valor_por_produto': {produto.id: 0 for produto in produtos},
                'total_geral_pecas': 0,
                'total_geral_valor': 0,
            }

        # Inicializa os dados da loja
        if loja_id not in vendas_por_loja:
            vendas_por_loja[loja_id] = {
                'loja': venda.loja,
                'total_por_produto': {produto.id: 0 for produto in produtos},
                'valor_por_produto': {produto.id: 0 for produto in produtos},
                'total_geral_pecas': 0,
                'total_geral_valor': 0,
            }

        # Atualiza os totais por vendedor
        vendas_por_vendedor[vendedor_id]['total_por_produto'][venda.produto.id] += venda.quantidade_vendida
        vendas_por_vendedor[vendedor_id]['total_geral_pecas'] += venda.quantidade_vendida

        # Atualiza os totais por loja
        vendas_por_loja[loja_id]['total_por_produto'][venda.produto.id] += venda.quantidade_vendida
        vendas_por_loja[loja_id]['total_geral_pecas'] += venda.quantidade_vendida
        
        # Ordenando as vendas por quantidade (mais vendido no topo)
        vendas_por_vendedor = dict(sorted(vendas_por_vendedor.items(), key=lambda item: item[1]['total_geral_pecas'], reverse=True))
        vendas_por_loja = dict(sorted(vendas_por_loja.items(), key=lambda item: item[1]['total_geral_pecas'], reverse=True))

        
    # Aplicação do acréscimo baseado no total de peças vendidas para vendedores
    for vendedor_id, dados in vendas_por_vendedor.items():
        total_pecas = dados['total_geral_pecas']            

        if 301 <= total_pecas <= 400:
            acrescimo = 0.25
        elif 401 <= total_pecas <= 500:
            acrescimo = 0.50
        elif 501 <= total_pecas <= 650:
            acrescimo = 0.75
        elif 651 <= total_pecas <= 800:
            acrescimo = 1.00
        elif 801 <= total_pecas <= 1000:
            acrescimo = 1.25
        elif total_pecas > 1001:
            acrescimo = 1.50
        else:
            acrescimo = 0  # Sem alteração se for <= 300

        # Atualiza os valores dos produtos e calcula o total por vendedor
        for produto in produtos:
            preco_base = produto.valor or 0
            preco_final = preco_base + acrescimo if preco_base <= 1.00 else preco_base
            valor_total_produto = dados['total_por_produto'][produto.id] * preco_final
            dados['valor_por_produto'][produto.id] = valor_total_produto
            dados['total_geral_valor'] += valor_total_produto

    # Calcula os totais gerais
    total_geral_pecas = sum(dados['total_geral_pecas'] for dados in vendas_por_vendedor.values())
    total_geral_valor = sum(dados['total_geral_valor'] for dados in vendas_por_vendedor.values())
    
    # Aplicação do acréscimo baseado no total de peças vendidas para lojas
    for loja_id, dados in vendas_por_loja.items():
        total_pecas = dados['total_geral_pecas']

        if 301 <= total_pecas <= 400:
            acrescimo = 0.25
        elif 401 <= total_pecas <= 500:
            acrescimo = 0.50
        elif 501 <= total_pecas <= 650:
            acrescimo = 0.75
        elif 651 <= total_pecas <= 800:
            acrescimo = 1.00
        elif 801 <= total_pecas <= 1000:
            acrescimo = 1.25
        elif total_pecas > 1001:
            acrescimo = 1.50
        else:
            acrescimo = 0  # Sem alteração se for <= 300

        # Atualiza os valores dos produtos e calcula o total por vendedor
        for produto in produtos:
            preco_base = produto.valor or 0
            preco_final = preco_base + acrescimo if preco_base <= 1.00 else preco_base
            valor_total_produto = dados['total_por_produto'][produto.id] * preco_final
            dados['valor_por_produto'][produto.id] = valor_total_produto
            dados['total_geral_valor'] += valor_total_produto

    # Calcula os totais gerais
    total_geral_pecas = sum(dados['total_geral_pecas'] for dados in vendas_por_loja.values())
    total_geral_valor = sum(dados['total_geral_valor'] for dados in vendas_por_loja.values())


    return render(request, "relatorio_vendas.html", {
        "ano_atual": ano_atual,
        "mes_atual": mes_atual,
        "anos_disponiveis": list(range(ano_atual, 2031)),
        "meses_disponiveis": range(1, 13),
        "vendas_por_vendedor": vendas_por_vendedor,
        "vendas_por_loja": vendas_por_loja, 
        "produtos": produtos,
        "total_geral_pecas": total_geral_pecas,
        "total_geral_valor": total_geral_valor,
        "ano": ano,
        "mes": mes,
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
    dia = request.GET.get('dia')  # Dia pode ser opcional

    # Obtém todas as vendas do mês/ano filtrado
    vendas = Venda.objects.filter(vendedor=vendedor, data_venda__year=ano, data_venda__month=mes)
    
        # Se o dia for informado, aplica o filtro também
    if dia:
        vendas = vendas.filter(data_venda__day=int(dia))

    # Obtém todos os produtos cadastrados
    produtos = Produto.objects.all()

    # Dicionário para armazenar vendas por dia e produto
    if dia:
        vendas_por_dia = {int(dia): {produto.id: 0 for produto in produtos}}
    else:
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
    if 301 <= total_geral_pecas <= 400:
        acrescimo = 0.25
    elif 401 <= total_geral_pecas <= 500:
        acrescimo = 0.50
    elif 501 <= total_geral_pecas <= 650:
        acrescimo = 0.75
    elif 651 <= total_geral_pecas <= 800:
        acrescimo = 1.00
    elif 801 <= total_geral_pecas <= 1000:
        acrescimo = 1.25
    elif total_geral_pecas > 1001:
        acrescimo = 1.50
    else:
        acrescimo = 0  # Sem alteração se for <= 300

    # Ajusta os valores dos produtos sem alterar o banco de dados
    for produto in produtos:
        preco_base = produto.valor or 0
        if preco_base <= 0.50:
            preco_final = preco_base + acrescimo
        else:
            preco_final = preco_base
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

    if dia:
        dias_formatados = {
        int(dia): DIAS_SEMANA.get(datetime.date(ano, mes, int(dia)).strftime("%A"), "Desconhecido")
        }
    else:
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
def editar_vendas(request, data):
    # Converte a data para o formato de data
    data_venda = datetime.datetime.strptime(data, "%Y-%m-%d").date()

    # Busca as vendas realizadas nesse dia para o vendedor logado
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