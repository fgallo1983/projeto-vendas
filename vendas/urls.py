from . import views
from django.urls import path


urlpatterns = [
    path('', views.index, name='index'),  # Página inicial (login)
    path('registrar_venda/', views.registrar_venda, name='registrar_venda'),
    path('pagina_vendas/', views.pagina_vendas, name='pagina_vendas'),  # Adicione essa linha
]