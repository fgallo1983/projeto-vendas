from . import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),  # Página inicial (login)
    path('home_vendedor/', views.home_vendedor, name='home_vendedor'),
    path('home_adm/', views.home_adm, name='home_adm'),
    path('registrar_venda/', views.registrar_venda, name='registrar_venda'),
    path('selos/', views.selos, name='selos'),  # Página de selos
    path('editar-venda/<int:venda_id>/', views.editar_venda, name='editar_venda'),
    path('apagar-venda/<int:venda_id>/', views.apagar_venda, name='apagar_venda'),
    path('relatorio_vendas/', views.relatorio_vendas, name='relatorio_vendas'),
    path('roteiros/', views.pagina_roteiros, name='roteiros'),
    path('enviar_roteiro/', views.enviar_roteiro, name='enviar_roteiro'),
    path('logout/', views.logout_view, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Servir arquivos de mídia no desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)