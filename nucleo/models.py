"""
Models do aplicativo Nucleo - NerdHub E-commerce

Este arquivo define todos os modelos de dados do sistema de e-commerce,
incluindo produtos, marcas, categorias, carrinho de compras, pedidos e reviews.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# ============================================
# MODELOS DE CATÁLOGO
# ============================================

class Marca(models.Model):
    """
    Modelo para armazenar marcas de produtos (PlayStation, Xbox, Nintendo, etc.)
    
    Atributos:
        nome: Nome da marca (ex: "PlayStation")
        logo: Imagem do logo da marca (opcional)
    """
    nome = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='marcas/', blank=True, null=True)

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"


class Categoria(models.Model):
    """
    Modelo para categorias de produtos (Consoles, Jogos, Acessórios, etc.)
    
    Atributos:
        nome: Nome da categoria
    """
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"


class Produto(models.Model):
    """
    Modelo principal de produto no catálogo
    
    Atributos:
        nome: Nome do produto
        descricao: Descrição detalhada do produto
        preco: Preço em formato decimal (ex: 199.90)
        imagem_principal: Imagem principal do produto
        marca: Relação com a marca (ForeignKey)
        categoria: Relação com a categoria (ForeignKey, opcional)
        criado_em: Data e hora de criação automática
    """
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)  # Permite valores até 999,999.99
    imagem_principal = models.ImageField(upload_to='produtos/')
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, null=True)
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='produtos'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    
    def media_avaliacoes(self):
        """Calcula a média das avaliações do produto"""
        reviews = self.reviews.all()
        if reviews.exists():
            return sum(review.nota for review in reviews) / reviews.count()
        return 0
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['-criado_em']  # Ordenar por mais recente primeiro


class ImagemProduto(models.Model):
    """
    Modelo para armazenar imagens adicionais de produtos
    
    Atributos:
        produto: Produto ao qual a imagem pertence
        imagem: Arquivo de imagem
    """
    produto = models.ForeignKey(Produto, related_name='imagens_adicionais', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='produtos/adicionais/')

    def __str__(self):
        return f"Imagem extra de {self.produto.nome}"
    
    class Meta:
        verbose_name = "Imagem do Produto"
        verbose_name_plural = "Imagens dos Produtos"


# ============================================
# MODELOS DE REVIEWS E AVALIAÇÕES
# ============================================

class Review(models.Model):
    """
    Modelo para reviews/avaliações de produtos pelos usuários
    
    Atributos:
        produto: Produto sendo avaliado
        usuario: Usuário que fez a avaliação
        comentario: Texto da review
        nota: Nota de 1 a 5 estrelas
        criado_em: Data e hora da review
    """
    produto = models.ForeignKey(Produto, related_name='reviews', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comentario = models.TextField()
    nota = models.PositiveIntegerField(
        default=5, 
        validators=[MinValueValidator(1), MaxValueValidator(5)]  # Validação: apenas 1-5
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.produto.nome} ({self.nota}⭐)"
    
    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-criado_em']  # Mais recentes primeiro


# ============================================
# MODELOS DE ESTOQUE
# ============================================

class Estoque(models.Model):
    """
    Modelo para controle de estoque de produtos
    
    Atributos:
        produto: Produto (OneToOne - cada produto tem um único estoque)
        quantidade: Quantidade disponível em estoque
    """
    produto = models.OneToOneField(Produto, on_delete=models.CASCADE, related_name='estoque')
    quantidade = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Estoque de {self.produto.nome}: {self.quantidade}"
    
    class Meta:
        verbose_name = "Estoque"
        verbose_name_plural = "Estoques"


# ============================================
# MODELOS DE CARRINHO DE COMPRAS
# ============================================

class Carrinho(models.Model):
    """
    Modelo para o carrinho de compras de cada usuário
    
    Atributos:
        usuario: Usuário dono do carrinho (OneToOne - cada usuário tem um carrinho)
    
    Nota: Os itens do carrinho são acessados via carrinho.itens.all()
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrinho')

    def __str__(self):
        return f"Carrinho de {self.usuario.username}"
    
    class Meta:
        verbose_name = "Carrinho"
        verbose_name_plural = "Carrinhos"


class ItemCarrinho(models.Model):
    """
    Modelo para itens individuais dentro do carrinho
    
    Atributos:
        carrinho: Carrinho ao qual o item pertence
        produto: Produto adicionado ao carrinho
        quantidade: Quantidade do produto no carrinho
    """
    carrinho = models.ForeignKey(Carrinho, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
    
    class Meta:
        verbose_name = "Item do Carrinho"
        verbose_name_plural = "Itens do Carrinho"


# ============================================
# MODELOS DE PEDIDOS
# ============================================

class Pedido(models.Model):
    """
    Modelo para pedidos finalizados
    
    Armazena todas as informações necessárias do pedido, incluindo:
    - Dados do usuário
    - Endereço de entrega completo
    - Forma de pagamento
    - Valor total
    - Status de finalização
    
    Atributos:
        usuario: Usuário que fez o pedido
        criado_em: Data e hora da criação do pedido
        finalizado: Boolean indicando se o pedido foi finalizado
        
        # Dados de endereço de entrega
        endereco_destinatario: Nome do destinatário
        endereco_rua: Nome da rua
        endereco_numero: Número do endereço
        endereco_complemento: Complemento (Apto, Bloco, etc.)
        endereco_bairro: Bairro
        endereco_cidade: Cidade
        endereco_estado: UF (2 letras)
        endereco_cep: CEP (formato: 00000-000)
        endereco_telefone: Telefone de contato
        
        # Dados de pagamento
        forma_pagamento: Método de pagamento escolhido
        total: Valor total do pedido
    """
    # Dados básicos do pedido
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)
    finalizado = models.BooleanField(default=False)
    
    # Dados de endereço de entrega
    endereco_destinatario = models.CharField(max_length=100, blank=True, verbose_name="Nome do destinatário")
    endereco_rua = models.CharField(max_length=200, blank=True, verbose_name="Rua")
    endereco_numero = models.CharField(max_length=10, blank=True, verbose_name="Número")
    endereco_complemento = models.CharField(max_length=100, blank=True, verbose_name="Complemento")
    endereco_bairro = models.CharField(max_length=100, blank=True, verbose_name="Bairro")
    endereco_cidade = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    endereco_estado = models.CharField(max_length=2, blank=True, verbose_name="Estado")
    endereco_cep = models.CharField(max_length=9, blank=True, verbose_name="CEP")
    endereco_telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    
    # Dados de pagamento
    FORMA_PAGAMENTO_CHOICES = [
        ('credito', 'Cartão de Crédito'),
        ('debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto Bancário'),
    ]
    forma_pagamento = models.CharField(
        max_length=20, 
        choices=FORMA_PAGAMENTO_CHOICES, 
        blank=True, 
        verbose_name="Forma de pagamento"
    )
    
    # Total do pedido
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total")

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-criado_em']  # Mais recentes primeiro


class ItemPedido(models.Model):
    """
    Modelo para itens individuais de um pedido
    
    Armazena uma cópia dos dados do produto no momento da compra,
    garantindo que mudanças futuras no preço não afetem pedidos antigos.
    
    Atributos:
        pedido: Pedido ao qual o item pertence
        produto: Produto comprado
        quantidade: Quantidade comprada
        preco_unitario: Preço do produto no momento da compra
    """
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} no Pedido #{self.pedido.id}"
    
    def get_subtotal(self):
        """Retorna o subtotal deste item (quantidade x preço unitário)"""
        return self.quantidade * self.preco_unitario
    
    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens dos Pedidos"