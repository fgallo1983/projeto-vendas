from django.urls import path
from . import views

urlpatterns = [
    path('registrar-venda/', views.registrar_venda, name='registrar_venda'),
    path('admin/', admin.site.urls),
    path('vendas/', include('vendas.urls')),
]