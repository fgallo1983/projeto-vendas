from . import views
from django.urls import path


urlpatterns = [
    path('pagina_vendas/', views.pagina_vendas, name='pagina_vendas'),  # Página de vendas
]