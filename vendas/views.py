from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login

def index(request):
    # Se o usuário já estiver autenticado, redireciona para a página de vendas ou página inicial.
    if request.user.is_authenticated:
        return redirect('registrar_venda.html')  # Ajuste para o nome da sua página de vendas

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # Realiza o login do usuário
            return redirect('registrar_venda.html')  # Redireciona para a página de vendas após o login bem-sucedido
    else:
        form = AuthenticationForm()

    return render(request, 'index.html', {'form': form})
