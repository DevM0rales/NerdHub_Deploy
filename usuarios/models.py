from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

# Create your models here.

class Perfil(models.Model):
    """
    Perfil do usuário com informações adicionais além do User padrão do Django
    """
    # Relacionamento com o usuário
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    
    # Identidade básica
    display_name = models.CharField(max_length=60, blank=True, verbose_name="Nome de exibição")
    first_name = models.CharField(max_length=30, blank=True, verbose_name="Primeiro nome")
    last_name = models.CharField(max_length=30, blank=True, verbose_name="Último nome")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Data de nascimento")
    
    GENDER_CHOICES = [
        ('male', 'Masculino'),
        ('female', 'Feminino'),
        ('other', 'Outro'),
        ('prefer_not', 'Prefiro não informar'),
    ]
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, blank=True, verbose_name="Gênero")
    
    # Documentos (dados sensíveis)
    cpf = models.CharField(max_length=14, blank=True, verbose_name="CPF")  # Formatado xxx.xxx.xxx-xx
    rg = models.CharField(max_length=20, blank=True, verbose_name="RG")
    
    DOCUMENT_TYPE_CHOICES = [
        ('CPF', 'CPF'),
        ('CNPJ', 'CNPJ'),
        ('PASSAPORTE', 'Passaporte'),
    ]
    document_type = models.CharField(max_length=15, choices=DOCUMENT_TYPE_CHOICES, blank=True, verbose_name="Tipo de documento")
    tax_id = models.CharField(max_length=20, blank=True, verbose_name="ID Fiscal")
    
    # Contato
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    phone_verified = models.BooleanField(default=False, verbose_name="Telefone verificado")
    secondary_email = models.EmailField(blank=True, verbose_name="Email secundário")
    
    CONTACT_METHOD_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('none', 'Nenhum'),
    ]
    preferred_contact_method = models.CharField(max_length=10, choices=CONTACT_METHOD_CHOICES, blank=True, verbose_name="Método de contato preferido")
    
    # Preferências & Perfil de compra
    LANGUAGE_CHOICES = [
        ('pt-BR', 'Português (Brasil)'),
        ('en-US', 'English (United States)'),
    ]
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='pt-BR', verbose_name="Idioma")
    
    CURRENCY_CHOICES = [
        ('BRL', 'Real Brasileiro'),
        ('USD', 'Dólar Americano'),
    ]
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='BRL', verbose_name="Moeda")
    
    newsletter_subscribed = models.BooleanField(default=False, verbose_name="Inscrito na newsletter")
    marketing_opt_in = models.BooleanField(default=False, verbose_name="Aceita comunicações de marketing")
    favorite_categories = models.TextField(blank=True, verbose_name="Categorias favoritas")  # Armazenar como JSON
    favorite_brands = models.TextField(blank=True, verbose_name="Marcas favoritas")  # Armazenar como JSON
    display_prices_with_tax = models.BooleanField(default=False, verbose_name="Exibir preços com impostos")
    receive_back_in_stock_alerts = models.BooleanField(default=True, verbose_name="Receber alertas de reposição")
    share_profile_with_community = models.BooleanField(default=False, verbose_name="Compartilhar perfil com a comunidade")
    
    # Social / Perfil público
    avatar_url = models.URLField(blank=True, verbose_name="URL do avatar")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biografia")
    social_links = models.TextField(blank=True, verbose_name="Links sociais")  # Armazenar como JSON
    preferred_display_style = models.CharField(
        max_length=20, 
        choices=[
            ('real_name', 'Nome real'),
            ('username', 'Nome de usuário'),
            ('display_name', 'Nome de exibição'),
        ], 
        default='username',
        verbose_name="Estilo de exibição preferido"
    )
    
    PROFILE_VISIBILITY_CHOICES = [
        ('private', 'Privado'),
        ('friends_only', 'Apenas amigos'),
        ('public', 'Público'),
    ]
    profile_visibility = models.CharField(max_length=15, choices=PROFILE_VISIBILITY_CHOICES, default='public', verbose_name="Visibilidade do perfil")
    show_order_history_public = models.BooleanField(default=False, verbose_name="Mostrar histórico de pedidos publicamente")
    
    # Comunidade / Gamificação
    wishlist = models.TextField(blank=True, verbose_name="Lista de desejos")  # Armazenar como JSON
    favorites = models.TextField(blank=True, verbose_name="Favoritos")  # Armazenar como JSON
    followers_count = models.IntegerField(default=0, verbose_name="Número de seguidores")
    following_count = models.IntegerField(default=0, verbose_name="Número de pessoas que segue")
    achievement_points = models.IntegerField(default=0, verbose_name="Pontos de conquista")
    badges = models.TextField(blank=True, verbose_name="Emblemas")  # Armazenar como JSON
    
    # Consentimentos & Legal
    terms_accepted = models.BooleanField(default=False, verbose_name="Termos aceitos")
    terms_accepted_at = models.DateTimeField(null=True, blank=True, verbose_name="Data de aceitação dos termos")
    privacy_policy_accepted = models.BooleanField(default=False, verbose_name="Política de privacidade aceita")
    privacy_policy_accepted_at = models.DateTimeField(null=True, blank=True, verbose_name="Data de aceitação da política de privacidade")
    marketing_consent = models.DateTimeField(null=True, blank=True, verbose_name="Consentimento de marketing")
    cookie_preferences = models.TextField(blank=True, verbose_name="Preferências de cookies")  # Armazenar como JSON
    data_deletion_request = models.BooleanField(default=False, verbose_name="Pedido de exclusão de dados")
    data_deletion_request_at = models.DateTimeField(null=True, blank=True, verbose_name="Data do pedido de exclusão")
    data_export_request = models.BooleanField(default=False, verbose_name="Pedido de exportação de dados")
    data_export_request_at = models.DateTimeField(null=True, blank=True, verbose_name="Data do pedido de exportação")
    
    # Admin / Moderation / Audit
    is_admin = models.BooleanField(default=False, verbose_name="É administrador")
    is_staff = models.BooleanField(default=False, verbose_name="É staff")
    
    ACCOUNT_STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('suspended', 'Suspenso'),
        ('banned', 'Banido'),
        ('pending_verification', 'Aguardando verificação'),
        ('closed', 'Fechado'),
    ]
    account_status = models.CharField(max_length=25, choices=ACCOUNT_STATUS_CHOICES, default='active', verbose_name="Status da conta")
    moderation_notes = models.TextField(blank=True, verbose_name="Notas de moderação")
    
    # Telemetria / Meta
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    last_login_at = models.DateTimeField(null=True, blank=True, verbose_name="Último login")
    last_order_at = models.DateTimeField(null=True, blank=True, verbose_name="Último pedido")
    preferred_device = models.CharField(
        max_length=10, 
        choices=[('mobile', 'Mobile'), ('desktop', 'Desktop')], 
        blank=True,
        verbose_name="Dispositivo preferido"
    )
    signup_source = models.CharField(max_length=50, blank=True, verbose_name="Fonte de cadastro")
    
    # Campos para integração com APIs externas
    oauth_provider = models.CharField(
        max_length=20, 
        choices=[('google', 'Google'), ('facebook', 'Facebook'), ('apple', 'Apple')], 
        blank=True,
        verbose_name="Provedor OAuth"
    )
    oauth_provider_id = models.CharField(max_length=100, blank=True, verbose_name="ID do provedor OAuth")
    payment_gateway_customer_id = models.CharField(max_length=100, blank=True, verbose_name="ID do cliente no gateway de pagamento")
    shipping_provider_customer_ref = models.CharField(max_length=100, blank=True, verbose_name="Referência do cliente no provedor de envio")
    
    # Extras específicos para e-commerce geek
    favorite_franchises = models.TextField(blank=True, verbose_name="Franquias favoritas")  # Armazenar como JSON
    shirt_size = models.CharField(
        max_length=5, 
        choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')], 
        blank=True,
        verbose_name="Tamanho de camiseta"
    )
    shoe_size = models.CharField(max_length=10, blank=True, verbose_name="Tamanho de sapato")
    collector_preferences = models.TextField(blank=True, verbose_name="Preferências de colecionador")  # Armazenar como JSON
    age_for_collectibles = models.IntegerField(null=True, blank=True, verbose_name="Idade para itens colecionáveis")
    want_notifications_for_new_releases = models.BooleanField(default=True, verbose_name="Quer notificações de novos lançamentos")
    preorder_opt_in = models.BooleanField(default=False, verbose_name="Aceita pré-encomendas")
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

class Endereco(models.Model):
    """
    Endereços do usuário
    """
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='enderecos')
    
    label = models.CharField(max_length=50, blank=True, verbose_name="Rótulo")  # Ex: Casa, Trabalho
    recipient_name = models.CharField(max_length=100, verbose_name="Nome do destinatário")
    street = models.CharField(max_length=200, verbose_name="Rua")
    number = models.CharField(max_length=10, verbose_name="Número")
    complement = models.CharField(max_length=100, blank=True, verbose_name="Complemento")
    neighborhood = models.CharField(max_length=100, verbose_name="Bairro")
    city = models.CharField(max_length=100, verbose_name="Cidade")
    state = models.CharField(max_length=2, verbose_name="Estado")  # UF
    country = models.CharField(max_length=50, default='Brasil', verbose_name="País")
    postal_code = models.CharField(max_length=9, verbose_name="CEP")  # Formatado xx.xxx-xxx
    phone_at_address = models.CharField(max_length=20, blank=True, verbose_name="Telefone no endereço")
    
    is_default_shipping = models.BooleanField(default=False, verbose_name="Endereço de entrega padrão")
    is_default_billing = models.BooleanField(default=False, verbose_name="Endereço de cobrança padrão")
    
    address_geolocation = models.TextField(blank=True, verbose_name="Geolocalização")  # Armazenar como JSON (lat/lng)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    def __str__(self):
        return f"{self.label or 'Endereço'} - {self.street}, {self.number}"
    
    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

class MetodoPagamento(models.Model):
    """
    Métodos de pagamento do usuário
    """
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='metodos_pagamento')
    
    PAYMENT_TYPE_CHOICES = [
        ('card', 'Cartão de crédito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto bancário'),
        ('paypal', 'PayPal'),
        ('applepay', 'Apple Pay'),
    ]
    
    type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, verbose_name="Tipo")
    card_brand = models.CharField(max_length=20, blank=True, verbose_name="Bandeira do cartão")
    card_last4 = models.CharField(max_length=4, blank=True, verbose_name="Últimos 4 dígitos do cartão")
    card_exp_month = models.CharField(max_length=2, blank=True, verbose_name="Mês de expiração")
    card_exp_year = models.CharField(max_length=4, blank=True, verbose_name="Ano de expiração")
    card_token = models.CharField(max_length=100, blank=True, verbose_name="Token do cartão")  # Sensível
    
    is_default = models.BooleanField(default=False, verbose_name="Método padrão")
    billing_address = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Endereço de cobrança")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    billing_info = models.TextField(blank=True, verbose_name="Informações de cobrança")  # Armazenar como JSON
    tax_exempt = models.BooleanField(default=False, verbose_name="Isento de impostos")
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.card_last4 or 'sem número'}"
    
    class Meta:
        verbose_name = "Método de pagamento"
        verbose_name_plural = "Métodos de pagamento"

class Sessao(models.Model):
    """
    Sessões do usuário para gerenciamento de dispositivos
    """
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='sessoes')
    
    token_id = models.CharField(max_length=100, unique=True, verbose_name="ID do token")
    issued_at = models.DateTimeField(default=timezone.now, verbose_name="Emitido em")
    expires_at = models.DateTimeField(verbose_name="Expira em")
    device_info = models.TextField(blank=True, verbose_name="Informações do dispositivo")
    ip_address = models.GenericIPAddressField(verbose_name="Endereço IP")
    
    def is_active(self):
        return timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Sessão de {self.perfil.user.username} - {self.ip_address}"
    
    class Meta:
        verbose_name = "Sessão"
        verbose_name_plural = "Sessões"

class Notificacao(models.Model):
    """
    Preferências de notificação do usuário
    """
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='notificacoes')
    
    order_updates = models.BooleanField(default=True, verbose_name="Atualizações de pedidos")
    promos = models.BooleanField(default=True, verbose_name="Promoções")
    back_in_stock = models.BooleanField(default=True, verbose_name="Alertas de reposição")
    reviews = models.BooleanField(default=True, verbose_name="Respostas a avaliações")
    system = models.BooleanField(default=True, verbose_name="Notificações do sistema")
    
    sms_opt_in = models.BooleanField(default=False, verbose_name="Aceita SMS")
    push_notifications_enabled = models.BooleanField(default=True, verbose_name="Notificações push habilitadas")
    
    def __str__(self):
        return f"Notificações de {self.perfil.user.username}"
    
    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

class Auditoria(models.Model):
    """
    Registro de ações sensíveis para auditoria
    """
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='auditorias')
    
    action = models.CharField(max_length=100, verbose_name="Ação")
    description = models.TextField(verbose_name="Descrição")
    ip_address = models.GenericIPAddressField(verbose_name="Endereço IP")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Criado em")
    
    def __str__(self):
        return f"{self.perfil.user.username} - {self.action} - {self.created_at}"
    
    class Meta:
        verbose_name = "Auditoria"
        verbose_name_plural = "Auditorias"