from django.urls import path
from . import views

urlpatterns = [
    path('registrar-venda/', views.registrar_venda, name='registrar_venda'),
]