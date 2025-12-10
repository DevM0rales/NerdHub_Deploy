from django.urls import path
from . import views

app_name = 'usuario'

urlpatterns = [
    
    path('conta/', views.conta, name='conta' ),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('sair/', views.user_logout, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/avatar/', views.upload_avatar, name='upload_avatar'),  # Added avatar upload endpoint
    path('perfil/seguranca/', views.perfil_seguranca, name='perfil_seguranca'),
    path('perfil/endereco/', views.perfil_endereco, name='perfil_endereco'),
    path('perfil/preferencias/', views.perfil_preferencias, name='perfil_preferencias'),
    path('perfil/privacidade/', views.perfil_privacidade, name='perfil_privacidade'),
    path('perfil/conta/', views.perfil_conta, name='perfil_conta'),
    path('enderecos/', views.enderecos, name='enderecos'),
    path('enderecos/adicionar/', views.endereco_adicionar, name='endereco_adicionar'),
    path('enderecos/editar/<int:endereco_id>/', views.endereco_editar, name='endereco_editar'),
    path('enderecos/atualizar/<int:endereco_id>/', views.endereco_atualizar, name='endereco_atualizar'),
    path('enderecos/excluir/<int:endereco_id>/', views.endereco_excluir, name='endereco_excluir'),
    path('enderecos/definir-principal/<int:endereco_id>/', views.endereco_definir_principal, name='endereco_definir_principal'),
    path('pedido/<int:pedido_id>/', views.pedido_detalhe, name='pedido_detalhe')
    
]