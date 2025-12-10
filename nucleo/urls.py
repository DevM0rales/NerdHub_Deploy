from django.urls import path, include
from . import views

app_name = 'nucleo'

urlpatterns = [
    path('', views.index, name='index'),
    # path('produto/<int:id>/', views.detalhe_produto, name='detalhe_produto'),
    path('sobre/', views.sobre, name='sobre'),
    path('suporte/', views.suporte, name='suporte'),
    path('usuario/', include('usuarios.urls'), name='usuarios'),
    path('marca/<str:marca_nome>/', views.produtos_por_marca, name='produtos_por_marca'),
    path('produto/<int:produto_id>/', views.detalhe_produto, name='detalhe_produto'),
    path('produto/<int:produto_id>/adicionar_carrinho/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('produto/<int:produto_id>/adicionar_review/', views.adicionar_review, name='adicionar_review'),

    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('carrinho/remover/<int:item_id>/', views.remover_item_carrinho, name='remover_item_carrinho'),
    path('carrinho/alterar_quantidade/<int:item_id>/', views.alterar_quantidade_carrinho, name='alterar_quantidade_carrinho'),
    path('checkout/', views.checkout, name='checkout'),
    path('carrinho/finalizar/', views.finalizar_pedido, name='finalizar_pedido'),
    
    # Admin - Product Management (mudado de /admin/ para /gerenciar/ para evitar conflito)
    path('gerenciar/produtos/', views.admin_produtos, name='admin_produtos'),
    path('gerenciar/produtos/adicionar/', views.admin_produto_adicionar, name='admin_produto_adicionar'),
    path('gerenciar/produtos/editar/<int:produto_id>/', views.admin_produto_editar, name='admin_produto_editar'),
    path('gerenciar/produtos/remover/<int:produto_id>/', views.admin_produto_remover, name='admin_produto_remover'),
    
    # Health check endpoints
    path('health/', views.health_check, name='health_check'),
    path('error-test/', views.error_test, name='error_test'),
]