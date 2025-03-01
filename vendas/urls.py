from . import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),  # Página inicial (login)
    path('registrar_venda/', views.registrar_venda, name='registrar_venda'),
    path('pagina_vendas/', views.pagina_vendas, name='pagina_vendas'),  # Adicione essa linha
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Servir arquivos de mídia no desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)