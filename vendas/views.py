from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login

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

    return render(request, 'registrar_venda.html')