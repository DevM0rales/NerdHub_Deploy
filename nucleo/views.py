"""
Views do aplicativo Nucleo - NerdHub E-commerce

Este arquivo contém todas as views (controladores) do sistema,
responsáveis por processar requisições e retornar respostas.
"""

from django.shortcuts import render, get_object_or_404, redirect
from .models import Produto, Review, Marca, Carrinho, ItemCarrinho, Pedido, Estoque, ItemPedido, Categoria
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.http import require_POST


# ============================================
# VIEWS PÚBLICAS - CATÁLOGO
# ============================================

def index(request):
    """
    View da página inicial / catálogo de produtos
    
    Exibe todos os produtos disponíveis em cards.
    Também passa todas as marcas para o menu dropdown.
    
    Args:
        request: HttpRequest object
        
    Returns:
        Renderiza template 'nucleo/index.html' com:
        - produtos: QuerySet de todos os produtos
        - marcas: QuerySet de todas as marcas
        - page_name: Identificador da página atual
    """
    produtos = Produto.objects.all()
    marcas = Marca.objects.all()
    return render(request, 'nucleo/index.html', {
        'produtos': produtos, 
        'marcas': marcas, 
        'page_name': 'index'
    })


def sobre(request):
    """
    View da página "Sobre"
    
    Exibe informações sobre a empresa NerdHub.
    
    Args:
        request: HttpRequest object
        
    Returns:
        Renderiza template 'nucleo/sobre.html'
    """
    return render(request, 'nucleo/sobre.html', {'page_name': 'sobre'})


def suporte(request):
    """
    View da página de Suporte
    
    Exibe FAQ e formulário de contato.
    
    Args:
        request: HttpRequest object
        
    Returns:
        Renderiza template 'nucleo/suporte.html'
    """
    return render(request, 'nucleo/suporte.html', {'page_name': 'suporte'})


def produtos_por_marca(request, marca_nome):
    """
    View para filtrar produtos por marca específica
    
    Busca produtos de uma marca específica (case-insensitive).
    Se a marca não existir, retorna 404.
    
    Args:
        request: HttpRequest object
        marca_nome: Nome da marca (str) vindo da URL
        
    Returns:
        Renderiza template 'nucleo/por_marca.html' com:
        - marca: Objeto Marca encontrado
        - produtos: QuerySet de produtos da marca
    """
    marca = get_object_or_404(Marca, nome__iexact=marca_nome)  # Case-insensitive
    produtos = Produto.objects.filter(marca=marca)
    return render(request, 'nucleo/por_marca.html', {
        'marca': marca, 
        'produtos': produtos
    })


def detalhe_produto(request, produto_id):
    """
    View de detalhes de um produto específico
    
    Exibe informações completas do produto, incluindo:
    - Dados do produto (nome, preço, descrição, imagens)
    - Reviews de usuários
    - Produtos relacionados da mesma marca
    
    Args:
        request: HttpRequest object
        produto_id: ID do produto (int) vindo da URL
        
    Returns:
        Renderiza template 'nucleo/detalhe_produto.html' com:
        - produto: Objeto Produto
        - relacionados: QuerySet de até 4 produtos da mesma marca
        - reviews: QuerySet de todas as reviews do produto
    """
    produto = get_object_or_404(Produto, id=produto_id)
    
    # Buscar produtos relacionados (mesma marca, exceto o atual, limit 4)
    relacionados = Produto.objects.filter(marca=produto.marca).exclude(id=produto.id)[:4]
    
    # Buscar todas as reviews do produto
    reviews = Review.objects.filter(produto=produto)
    
    return render(request, 'nucleo/detalhe_produto.html', {
        'produto': produto,
        'relacionados': relacionados,
        'reviews': reviews
    })


# ============================================
# VIEWS DE CARRINHO - REQUER LOGIN
# ============================================

@login_required
def adicionar_ao_carrinho(request, produto_id):
    """
    Adiciona um produto ao carrinho do usuário
    
    Lógica:
    1. Verifica se o produto existe
    2. Verifica disponibilidade em estoque (se houver controle)
    3. Cria carrinho se não existir
    4. Se item já existe no carrinho, incrementa quantidade
    5. Se item novo, adiciona com quantidade 1
    
    Args:
        request: HttpRequest object (deve ter usuário autenticado)
        produto_id: ID do produto (int) vindo da URL
        
    Returns:
        Redirect para página de detalhes do produto
        Mensagens: success (item adicionado) ou error (sem estoque)
    """
    produto = get_object_or_404(Produto, id=produto_id)
    
    # Verificar se o produto tem estoque (opcional)
    # Se não houver registro de estoque, permitir adicionar ao carrinho
    estoque = None
    try:
        estoque = produto.estoque
    except:
        # Se não houver estoque cadastrado, continuar normalmente
        pass
    
    # Obter ou criar carrinho do usuário
    carrinho, created = Carrinho.objects.get_or_create(usuario=request.user)
    
    # Obter ou criar item no carrinho
    item, created = ItemCarrinho.objects.get_or_create(carrinho=carrinho, produto=produto)
    
    if not created:
        # Item já existe no carrinho, incrementar quantidade
        # Se houver controle de estoque, verificar disponibilidade
        if estoque and estoque.quantidade <= item.quantidade:
            messages.error(request, "Quantidade indisponível em estoque!")
        else:
            item.quantidade += 1
            item.save()
            messages.success(request, "Quantidade atualizada no carrinho!")
    else:
        # Item novo, definir quantidade inicial
        item.quantidade = 1
        item.save()
        messages.success(request, "Produto adicionado ao carrinho!")
    
    return redirect('nucleo:detalhe_produto', produto_id=produto.id)


@login_required
def adicionar_review(request, produto_id):
    """
    Adiciona uma review/avaliação de produto
    
    Apenas aceita requisições POST.
    Cria uma nova review associada ao produto e usuário.
    
    Args:
        request: HttpRequest object (POST com 'texto' e 'nota')
        produto_id: ID do produto (int) vindo da URL
        
    Returns:
        Redirect para página de detalhes do produto
        Mensagem: success (review adicionada)
    """
    if request.method == "POST":
        produto = get_object_or_404(Produto, id=produto_id)
        
        # Obter dados do formulário
        texto = request.POST.get("texto")
        nota = request.POST.get("nota")
        
        # Validar e converter nota para inteiro (default: 5)
        if nota:
            nota = int(nota)
        else:
            nota = 5
        
        # Criar nova review
        Review.objects.create(
            produto=produto, 
            usuario=request.user, 
            comentario=texto, 
            nota=nota
        )
        
        messages.success(request, "Review adicionada com sucesso!")
    
    return redirect('nucleo:detalhe_produto', produto_id=produto_id)


@login_required
def ver_carrinho(request):
    """
    Exibe o carrinho de compras do usuário
    
    Calcula o total de cada item e o total geral do carrinho.
    Também obtém produtos sugeridos para exibir abaixo do carrinho.
    
    Args:
        request: HttpRequest object (usuário autenticado)
        
    Returns:
        Renderiza template 'nucleo/carrinho.html' com:
        - itens_com_total: Lista de dicts com item e total calculado
        - total: Total geral do carrinho (Decimal)
        - produtos_sugeridos: Produtos recomendados para exibir sugestões
    """
    # Obter ou criar carrinho para o usuário
    carrinho, created = Carrinho.objects.get_or_create(usuario=request.user)
    itens = carrinho.itens.all()
    
    # Calcular o total para cada item e o total geral
    itens_com_total = []
    total_geral = 0
    
    for item in itens:
        total_item = item.produto.preco * item.quantidade
        total_geral += total_item
        itens_com_total.append({
            'item': item,
            'total': total_item
        })
    
    # Obter produtos sugeridos (excluindo os que já estão no carrinho)
    produtos_no_carrinho = [item.produto.id for item in itens]
    produtos_sugeridos = Produto.objects.exclude(id__in=produtos_no_carrinho)[:8]  # Limitar a 8 produtos
    
    return render(request, 'nucleo/carrinho.html', {
        'itens_com_total': itens_com_total,
        'total': total_geral,
        'produtos_sugeridos': produtos_sugeridos
    })


@login_required
@require_POST
def alterar_quantidade_carrinho(request, item_id):
    """
    Altera a quantidade de um item no carrinho
    
    Args:
        request: HttpRequest object (usuário autenticado)
        item_id: ID do ItemCarrinho (int) vindo da URL
        
    Returns:
        JsonResponse com status de sucesso ou erro
    """
    item = get_object_or_404(ItemCarrinho, id=item_id)
    
    # Verificar se o item pertence ao carrinho do usuário (segurança)
    if item.carrinho.usuario != request.user:
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    acao = request.POST.get('acao')
    
    if acao == 'aumentar':
        item.quantidade += 1
        item.save()
        return JsonResponse({'success': True, 'nova_quantidade': item.quantidade})
    elif acao == 'diminuir':
        if item.quantidade > 1:
            item.quantidade -= 1
            item.save()
            return JsonResponse({'success': True, 'nova_quantidade': item.quantidade})
        else:
            return JsonResponse({'success': False, 'error': 'Quantidade mínima atingida'}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Ação inválida'}, status=400)


@login_required
def remover_item_carrinho(request, item_id):
    """
    Remove um item específico do carrinho
    
    Verifica se o item pertence ao carrinho do usuário antes de remover.
    
    Args:
        request: HttpRequest object (usuário autenticado)
        item_id: ID do ItemCarrinho (int) vindo da URL
        
    Returns:
        Redirect para página do carrinho
        Mensagens: success (item removido) ou error (sem permissão)
    """
    item = get_object_or_404(ItemCarrinho, id=item_id)
    
    # Verificar se o item pertence ao carrinho do usuário (segurança)
    if item.carrinho.usuario == request.user:
        item.delete()
        messages.success(request, "Item removido do carrinho!")
    else:
        messages.error(request, "Você não tem permissão para remover este item!")
    
    return redirect('nucleo:ver_carrinho')

# ============================================
# VIEWS DE CHECKOUT E FINALIZAÇÃO
# ============================================

@login_required
def checkout(request):
    """
    Página de checkout - formulário de finalização do pedido
    
    Exibe formulário para o usuário preencher:
    - Endereço de entrega (com opção de usar endereços salvos)
    - Forma de pagamento
    - Resumo do pedido
    
    Args:
        request: HttpRequest object (usuário autenticado)
        
    Returns:
        Renderiza template 'nucleo/checkout.html' com:
        - itens_com_total: Lista de itens do carrinho com totais
        - total: Total geral do pedido
        - enderecos_salvos: Endereços do perfil do usuário (se existir)
        
    Redirects:
        - Para 'index' se carrinho estiver vazio
    """
    # Obter carrinho do usuário
    carrinho, created = Carrinho.objects.get_or_create(usuario=request.user)
    itens = carrinho.itens.all()
    
    # Verificar se carrinho tem itens
    if not itens.exists():
        messages.info(request, "Seu carrinho está vazio!")
        return redirect('nucleo:index')
    
    # Calcular o total do pedido
    total_geral = sum(item.produto.preco * item.quantidade for item in itens)
    
    # Buscar endereços salvos do usuário (se tiver perfil)
    enderecos_salvos = []
    try:
        if hasattr(request.user, 'perfil'):
            enderecos_salvos = request.user.perfil.enderecos.all()
    except:
        pass
    
    # Preparar lista de itens com totais calculados
    itens_com_total = []
    for item in itens:
        total_item = item.produto.preco * item.quantidade
        itens_com_total.append({
            'item': item,
            'total': total_item
        })
    
    return render(request, 'nucleo/checkout.html', {
        'itens_com_total': itens_com_total,
        'total': total_geral,
        'enderecos_salvos': enderecos_salvos
    })


@login_required
def finalizar_pedido(request):
    """
    Processa a finalização do pedido com todos os dados
    
    Recebe dados do formulário de checkout via POST e:
    1. Valida que o carrinho não está vazio
    2. Calcula o total do pedido
    3. Cria o pedido com todos os dados (endereço, pagamento, total)
    4. Cria itens do pedido com preços fixados
    5. Atualiza estoque (se houver controle)
    6. Limpa o carrinho
    
    Args:
        request: HttpRequest object (POST com dados do formulário)
            Campos esperados:
            - endereco_destinatario, endereco_rua, endereco_numero
            - endereco_complemento, endereco_bairro, endereco_cidade
            - endereco_estado, endereco_cep, endereco_telefone
            - forma_pagamento
        
    Returns:
        Redirect para 'checkout' se não for POST
        Redirect para 'index' após finalizar com sucesso
        Mensagens: success (pedido criado) ou info (carrinho vazio)
        
    Nota:
        - Preços dos produtos são fixados no momento da compra
        - Estoque é decrementado se houver controle cadastrado
        - Carrinho é completamente limpo após finalização
    """
    # Aceitar apenas requisições POST
    if request.method != 'POST':
        return redirect('nucleo:checkout')
    
    # Obter carrinho e itens
    carrinho, created = Carrinho.objects.get_or_create(usuario=request.user)
    itens = carrinho.itens.all()
    
    # Verificar se carrinho tem itens
    if not itens.exists():
        messages.info(request, "Seu carrinho está vazio!")
        return redirect('nucleo:index')
    
    # Calcular o total do pedido
    total_geral = sum(item.produto.preco * item.quantidade for item in itens)
    
    # Criar o pedido com dados de endereço e pagamento
    pedido = Pedido.objects.create(
        usuario=request.user,
        total=total_geral,
        # Dados de endereço vindos do formulário
        endereco_destinatario=request.POST.get('endereco_destinatario', ''),
        endereco_rua=request.POST.get('endereco_rua', ''),
        endereco_numero=request.POST.get('endereco_numero', ''),
        endereco_complemento=request.POST.get('endereco_complemento', ''),
        endereco_bairro=request.POST.get('endereco_bairro', ''),
        endereco_cidade=request.POST.get('endereco_cidade', ''),
        endereco_estado=request.POST.get('endereco_estado', ''),
        endereco_cep=request.POST.get('endereco_cep', ''),
        endereco_telefone=request.POST.get('endereco_telefone', ''),
        # Dados de pagamento
        forma_pagamento=request.POST.get('forma_pagamento', ''),
        finalizado=True
    )
    
    # Processar cada item do carrinho
    for item in itens:
        # Atualizar a quantidade no estoque (se houver controle)
        try:
            estoque = item.produto.estoque
            if estoque.quantidade >= item.quantidade:
                estoque.quantidade -= item.quantidade
                estoque.save()
            else:
                # Não há estoque suficiente, mas continuamos com o pedido
                pass
        except:
            # Produto sem estoque controlado, continuar normalmente
            pass
        
        # Criar item do pedido com preço fixado
        # (garantindo que mudanças futuras no preço não afetem este pedido)
        ItemPedido.objects.create(
            pedido=pedido,
            produto=item.produto,
            quantidade=item.quantidade,
            preco_unitario=item.produto.preco  # Preço no momento da compra
        )
    
    # Limpar o carrinho
    itens.delete()
    
    messages.success(request, f"Pedido #{pedido.id} finalizado com sucesso!")
    
    return redirect('nucleo:index')

# ============================================
# VIEWS DE ADMINISTRAÇÃO - GERENCIAMENTO DE PRODUTOS
# Apenas superusuários têm acesso a estas views
# ============================================

@login_required
def admin_produtos(request):
    """
    Lista todos os produtos para gerenciamento
    
    Permite ao administrador visualizar todos os produtos cadastrados.
    Também fornece marcas e categorias para filtros/formulários.
    
    Args:
        request: HttpRequest object (usuário autenticado)
        
    Returns:
        Renderiza template 'nucleo/admin_produtos.html' com:
        - produtos: QuerySet de todos os produtos (ordenado por criação)
        - marcas: QuerySet de todas as marcas
        - categorias: QuerySet de todas as categorias
        
    Raises:
        PermissionDenied: Se o usuário não for superuser
    """
    # Verificar permissão de administrador
    if not request.user.is_superuser:
        raise PermissionDenied
    
    # Buscar todos os produtos (mais recentes primeiro)
    produtos = Produto.objects.all().order_by('-criado_em')
    marcas = Marca.objects.all()
    categorias = Categoria.objects.all()
    
    return render(request, 'nucleo/admin_produtos.html', {
        'produtos': produtos,
        'marcas': marcas,
        'categorias': categorias
    })


@login_required
def admin_produto_adicionar(request):
    """
    Adiciona um novo produto ao catálogo
    
    Aceita formulário com dados do produto e cria:
    - Produto novo
    - Estoque inicial para o produto
    
    GET: Exibe formulário vazio
    POST: Processa dados e cria produto
    
    Args:
        request: HttpRequest object
            POST esperado:
            - nome: Nome do produto (obrigatório)
            - descricao: Descrição do produto
            - preco: Preço (obrigatório)
            - marca: ID da marca
            - categoria: ID da categoria
            - imagem_principal: Arquivo de imagem (obrigatório)
            - quantidade_estoque: Quantidade inicial em estoque
        
    Returns:
        GET: Renderiza 'nucleo/admin_produto_form.html' com marcas e categorias
        POST: Redirect para 'admin_produtos' ou 'perfil' (conforme parâmetro 'next')
        Mensagens: success (produto criado) ou error (dados inválidos)
        
    Raises:
        PermissionDenied: Se o usuário não for superuser
    """
    # Verificar permissão de administrador
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == 'POST':
        # Obter dados do formulário
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')
        preco = request.POST.get('preco')
        marca_id = request.POST.get('marca')
        categoria_id = request.POST.get('categoria')
        imagem_principal = request.FILES.get('imagem_principal')
        
        # Validação básica dos campos obrigatórios
        if not nome or not preco or not imagem_principal:
            messages.error(request, "Nome, preço e imagem são obrigatórios!")
            # Verificar de onde veio a requisição
            next_url = request.GET.get('next', 'nucleo:admin_produtos')
            return redirect(next_url)
        
        # Criar produto
        produto = Produto.objects.create(
            nome=nome,
            descricao=descricao,
            preco=preco,
            imagem_principal=imagem_principal,
            marca_id=marca_id if marca_id else None,
            categoria_id=categoria_id if categoria_id else None
        )
        
        # Criar estoque inicial
        quantidade_estoque = request.POST.get('quantidade_estoque', 0)
        Estoque.objects.create(produto=produto, quantidade=quantidade_estoque)
        
        messages.success(request, f"Produto '{nome}' adicionado com sucesso!")
        
        # Verificar de onde veio a requisição para redirecionar corretamente
        next_url = request.GET.get('next')
        if next_url == 'perfil':
            return redirect('usuario:perfil')
        return redirect('nucleo:admin_produtos')
    
    # GET: Exibir formulário vazio
    marcas = Marca.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'nucleo/admin_produto_form.html', {
        'marcas': marcas,
        'categorias': categorias
    })


@login_required
def admin_produto_editar(request, produto_id):
    """
    Edita um produto existente
    
    Permite atualizar todos os dados do produto, incluindo:
    - Informações básicas (nome, descrição, preço)
    - Marca e categoria
    - Imagem principal
    - Quantidade em estoque
    
    GET: Exibe formulário preenchido com dados atuais
    POST: Processa atualizações
    
    Args:
        request: HttpRequest object
            POST esperado:
            - nome, descricao, preco: Dados básicos
            - marca, categoria: IDs de relacionamentos
            - imagem_principal: Nova imagem (opcional)
            - quantidade_estoque: Nova quantidade
        produto_id: ID do produto a ser editado
        
    Returns:
        GET: Renderiza 'nucleo/admin_produto_form.html' com dados do produto
        POST: Redirect para 'admin_produtos'
        Mensagens: success (produto atualizado)
        
    Raises:
        PermissionDenied: Se o usuário não for superuser
        Http404: Se o produto não existir
    """
    # Verificar permissão de administrador
    if not request.user.is_superuser:
        raise PermissionDenied
    
    # Buscar produto ou retornar 404
    produto = get_object_or_404(Produto, id=produto_id)
    
    if request.method == 'POST':
        # Atualizar dados básicos
        produto.nome = request.POST.get('nome', produto.nome)
        produto.descricao = request.POST.get('descricao', produto.descricao)
        produto.preco = request.POST.get('preco', produto.preco)
        
        # Atualizar marca se fornecida
        marca_id = request.POST.get('marca')
        if marca_id:
            produto.marca_id = marca_id
        
        # Atualizar categoria se fornecida
        categoria_id = request.POST.get('categoria')
        if categoria_id:
            produto.categoria_id = categoria_id
        
        # Atualizar imagem se uma nova foi enviada
        imagem_principal = request.FILES.get('imagem_principal')
        if imagem_principal:
            produto.imagem_principal = imagem_principal
        
        # Salvar alterações do produto
        produto.save()
        
        # Atualizar estoque
        quantidade_estoque = request.POST.get('quantidade_estoque')
        if quantidade_estoque is not None:
            # Criar ou atualizar estoque
            estoque, created = Estoque.objects.get_or_create(produto=produto)
            estoque.quantidade = quantidade_estoque
            estoque.save()
        
        messages.success(request, f"Produto '{produto.nome}' atualizado com sucesso!")
        return redirect('nucleo:admin_produtos')
    
    # GET: Obter dados atuais para preencher formulário
    estoque = None
    try:
        estoque = produto.estoque
    except:
        pass
    
    marcas = Marca.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'nucleo/admin_produto_form.html', {
        'produto': produto,
        'estoque': estoque,
        'marcas': marcas,
        'categorias': categorias
    })


@login_required
def admin_produto_remover(request, produto_id):
    """
    Remove um produto do catálogo
    
    Deleta permanentemente o produto e seus relacionamentos:
    - Estoque associado
    - Imagens adicionais
    - Reviews (dependendo da configuração CASCADE)
    
    Args:
        request: HttpRequest object (usuário autenticado)
        produto_id: ID do produto a ser removido
        
    Returns:
        Redirect para 'admin_produtos'
        Mensagem: success (produto removido)
        
    Raises:
        PermissionDenied: Se o usuário não for superuser
        Http404: Se o produto não existir
        
    Aviso:
        Esta ação é irreversível!
    """
    # Verificar permissão de administrador
    if not request.user.is_superuser:
        raise PermissionDenied
    
    # Buscar produto ou retornar 404
    produto = get_object_or_404(Produto, id=produto_id)
    nome_produto = produto.nome
    
    # Deletar produto (cascade deleta relacionamentos)
    produto.delete()
    
    messages.success(request, f"Produto '{nome_produto}' removido com sucesso!")
    return redirect('nucleo:admin_produtos')