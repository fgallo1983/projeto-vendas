from . import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView, error_404_view
from django.conf.urls import handler404


urlpatterns = [
    path('', views.index, name='index'),  # Página inicial (login)
    path('home_vendedor/', views.home_vendedor, name='home_vendedor'),
    path('home_adm/', views.home_adm, name='home_adm'),
    path("vendedoras/", views.listar_vendedoras, name="listar_vendedoras"),
    path("vendedoras/<int:pk>/editar/", views.editar_vendedora, name="editar_vendedora"),
    path("vendedoras/<int:pk>/status/", views.alternar_status_vendedora, name="alternar_status_vendedora"),
    path('registrar_venda/', views.registrar_venda, name='registrar_venda'),
    path('registrar-venda/<int:id_vendedor>/', views.registrar_venda, name='registrar_venda'),
    path('ajax/lojas/', views.carregar_lojas_por_vendedora, name='carregar_lojas_por_vendedora'),
    path('selos/', views.selos, name='selos'),  # Página de selos
    path('selos/<int:id_vendedor>/', views.selos, name='selos'),  # Para admin visualizar de outro vendedor
    path('editar-venda/<int:id_vendedor>/<str:data>/', views.editar_vendas, name='editar_vendas'),
    path('apagar-venda/<int:venda_id>/', views.apagar_venda, name='apagar_venda'),
    path("metas/", views.listar_metas, name="listar_metas"),
    path("metas/adicionar/", views.adicionar_meta, name="adicionar_meta"),
    path("metas/editar/<int:meta_id>/", views.editar_meta, name="editar_meta"),
    path("metas/excluir/<int:meta_id>/", views.excluir_meta, name="excluir_meta"),
    path('relatorio_vendas/', views.relatorio_vendas, name='relatorio_vendas'),
    path('roteiros/', views.pagina_roteiros, name='roteiros'),
    path('enviar_roteiro/', views.enviar_roteiro, name='enviar_roteiro'),
    path('excluir_roteiro/<int:roteiro_id>/', views.excluir_roteiro, name='excluir_roteiro'),
    path('logout/', views.logout_view, name='logout'),
    path('esqueci-minha-senha/', CustomPasswordResetView.as_view(), name='custom_password_reset'),
    path('esqueci-minha-senha/success/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), 
         name='password_reset_done'),
    path('esqueci-minha-senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), 
         name='password_reset_confirm'),
    path('esqueci-minha-senha/completar/', auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), 
         name='password_reset_complete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Servir arquivos de mídia no desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
handler404 = error_404_view