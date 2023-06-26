from django.urls import path
from . import views

urlpatterns = [
    path('lista_cliente/', views.lista_cliente, name='lista_cliente'),
    path('cliente/cadastrar/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('cliente/editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('deletar_cliente/<int:id>/', views.deletar_cliente, name='deletar_cliente'),
    path('cliente/<int:id>/add_value_to_limit/', views.add_value_to_limit, name='add_value_to_limit'),
]
