from django.urls import path
from . import views


urlpatterns = [
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/create/', views.categoria_create, name='categoria_create'),
    path('produtos/lista/', views.lista_produtos, name='lista_produtos'),
    path('produtos/create/', views.cadastra_atualiza_produto, name='cadastra_atualiza_produto'),
    path('produtos/venda/', views.venda_produto, name='venda_produto'),
    path('finalizar_venda/', views.finalizar_venda, name='finalizar_venda'),
    path('produtos/edita/<int:pk>/', views.edita_produto, name='edita_produto'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('listar_vendas/', views.listar_vendas, name='listar_vendas'),
    path('remover_item_carrinho/<int:item_index>/', views.remover_item_carrinho, name='remover_item_carrinho'),
    path('buscar_produto/', views.buscar_produto, name='buscar_produto'),
]
