from . import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView


urlpatterns = [
    path('', views.index, name='index'),  # Página inicial (login)
    path('home_vendedor/', views.home_vendedor, name='home_vendedor'),
    path('home_adm/', views.home_adm, name='home_adm'),
    path('registrar_venda/', views.registrar_venda, name='registrar_venda'),
    path('selos/', views.selos, name='selos'),  # Página de selos
    path('selos/<int:id_vendedor>/', views.selos, name='selos'),  # Para admin visualizar de outro vendedor
    path('editar_vendas/<str:data>/', views.editar_vendas, name='editar_vendas'),
    path('apagar-venda/<int:venda_id>/', views.apagar_venda, name='apagar_venda'),
    path('relatorio_vendas/', views.relatorio_vendas, name='relatorio_vendas'),
    path('roteiros/', views.pagina_roteiros, name='roteiros'),
    path('enviar_roteiro/', views.enviar_roteiro, name='enviar_roteiro'),
    path('excluir_roteiro/<int:roteiro_id>/', views.excluir_roteiro, name='excluir_roteiro'),
    path('logout/', views.logout_view, name='logout'),
    path('esqueci-minha-senha/', CustomPasswordResetView.as_view(), name='password_reset'),
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