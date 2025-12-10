"""
Views do aplicativo Usuarios - NerdHub E-commerce

Este arquivo contém todas as views relacionadas à autenticação e
gerenciamento de perfis de usuários.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid
from PIL import Image
from io import BytesIO
from .models import Perfil, Endereco
from nucleo.models import Produto, Marca, Categoria, Pedido


# ============================================
# VIEWS DE AUTENTICAÇÃO
# ============================================

def conta(request):
    """
    View para login de usuários
    
    GET: Exibe formulário de login
    POST: Processa autenticação
    
    Args:
        request: HttpRequest object
            POST esperado:
            - username: Nome de usuário
            - senha: Senha do usuário
            
    Returns:
        GET: Renderiza 'usuarios/conta.html'
        POST: Redirect para 'index' (ou parâmetro 'next') se sucesso
              Renderiza formulário novamente se falha
        Mensagens: success (login realizado) ou error (credenciais inválidas)
        
    Nota:
        - Se usuário já estiver autenticado, redireciona automaticamente
        - Atualiza last_login_at no perfil do usuário
        - Suporta parâmetro 'next' para redirect após login
    """
    if request.method == "GET":
        # Se usuário já está autenticado, redirecionar para index
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Verificar se há parâmetro next
            next_url = request.GET.get('next', 'nucleo:index')
            if next_url == 'nucleo:index' or not next_url:
                return redirect('nucleo:index')
            else:
                return redirect(next_url)
        return render(request, 'usuarios/conta.html')
    else:
        # POST: Processar login
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        
        # Tentar autenticar usuário
        user = authenticate(username=username, password=senha)
        
        if user:
            # Login bem-sucedido
            login(request, user)
            messages.success(request, "Login realizado com sucesso!")
            
            # Atualizar timestamp de último login
            if hasattr(user, 'perfil'):
                user.perfil.last_login_at = timezone.now()
                user.perfil.save()
            
            # Verificar se há parâmetro next para redirecionamento
            next_url = request.GET.get('next', 'nucleo:index')
            # Evitar loops de redirect para páginas de autenticação
            if next_url and ('conta' in str(next_url) or 'cadastro' in str(next_url)):
                next_url = 'nucleo:index'
            return redirect(next_url)
        else:
            # Falha na autenticação
            messages.error(request, "Usuário ou senha inválidos!")
            return render(request, 'usuarios/conta.html')


def cadastro(request):
    """
    View para cadastro de novos usuários
    
    GET: Exibe formulário de cadastro
    POST: Processa criação de novo usuário
    
    Args:
        request: HttpRequest object
            POST esperado:
            - username: Nome de usuário (único)
            - email: Email do usuário (único)
            - senha: Senha
            
    Returns:
        GET: Renderiza 'usuarios/cadastro.html'
        POST: Redirect para 'index' se sucesso
              Renderiza formulário novamente se falha
        Mensagens: success (cadastro realizado) ou error (dados duplicados)
        
    Validações:
        - Username deve ser único
        - Email deve ser único
        
    Nota:
        - Se usuário já estiver autenticado, redireciona automaticamente
        - Após cadastro, usuário é automaticamente autenticado
    """
    if request.method == "GET":
        # Se usuário já está autenticado, redirecionar para index
        if hasattr(request, 'user') and request.user.is_authenticated:
            return redirect('nucleo:index')
        return render(request, 'usuarios/cadastro.html')
    else:
        # POST: Processar cadastro
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        # Verificar se username já existe
        if User.objects.filter(username=username).exists():
            messages.error(request, "Já existe um usuário com este nome!")
            return render(request, 'usuarios/cadastro.html')
        
        # Verificar se email já existe
        if User.objects.filter(email=email).exists():
            messages.error(request, "Já existe um usuário com este email!")
            return render(request, 'usuarios/cadastro.html')
        
        # Criar novo usuário
        user = User.objects.create_user(username=username, email=email, password=senha)
        messages.success(request, "Usuário cadastrado com sucesso!")
        
        # Fazer login automático após cadastro
        login(request, user)
        return redirect('nucleo:index')


def user_logout(request):
    """
    View para logout do usuário
    
    Encerra a sessão atual do usuário.
    
    Args:
        request: HttpRequest object
        
    Returns:
        Redirect para 'index'
        Mensagem: success (logout realizado)
    """
    logout(request)
    messages.success(request, "Você saiu da sua conta!")
    return redirect('nucleo:index')

# ============================================
# VIEWS DE PERFIL - REQUER LOGIN
# ============================================

@login_required
def perfil(request):
    """
    View principal do perfil do usuário
    
    Exibe e permite editar:
    - Informações pessoais (nome, telefone, data de nascimento, gênero)
    - Alterar senha
    - Visualizar endereços
    - Visualizar histórico de pedidos
    - [Superuser] Gerenciar produtos, marcas e categorias
    
    GET: Exibe página de perfil com todas as abas
    POST: Processa atualizações de perfil ou alteração de senha
    
    Args:
        request: HttpRequest object (usuário autenticado)
            POST pode conter:
            - Para atualização de perfil: display_name, full_name, phone, birth_date, gender
            - Para alteração de senha: current_password, new_password, confirm_password
            
    Returns:
        Renderiza 'usuarios/perfil.html' com:
        - perfil: Objeto Perfil do usuário
        - pedidos: QuerySet de pedidos do usuário (com prefetch de itens)
        - enderecos: QuerySet de endereços do usuário
        - [Se superuser] marcas, categorias, produtos
        
    Nota:
        - Cria perfil automaticamente se não existir
        - Usa prefetch_related para otimizar consultas de pedidos
        - Mantém usuário logado após alteração de senha (update_session_auth_hash)
    """
    # Obter ou criar perfil para usuários que não têm um
    perfil, created = Perfil.objects.get_or_create(user=request.user)  # type: ignore
    
    if request.method == "POST":
        # Verificar se é uma requisição de alteração de senha
        if 'change_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Verificar se a senha atual está correta
            if not request.user.check_password(current_password):
                messages.error(request, "Senha atual incorreta!")
                return redirect('usuario:perfil')  # Redirect to perfil view instead
            
            # Verificar se as novas senhas coincidem
            if new_password != confirm_password:
                messages.error(request, "As novas senhas não coincidem!")
                return redirect('usuario:perfil')  # Redirect to perfil view instead
            
            # Verificar se a nova senha tem pelo menos 8 caracteres
            if len(new_password) < 8:
                messages.error(request, "A nova senha deve ter pelo menos 8 caracteres!")
                return redirect('usuario:perfil')  # Redirect to perfil view instead
            
            # Verificar se a nova senha atende aos requisitos de complexidade
            import re
            if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', new_password):
                messages.error(request, "A nova senha deve conter pelo menos uma letra maiúscula, uma letra minúscula e um número!")
                return redirect('usuario:perfil')  # Redirect to perfil view instead
            
            # Alterar a senha
            request.user.set_password(new_password)
            request.user.save()
            # Manter o usuário logado após alteração de senha
            update_session_auth_hash(request, request.user)
            messages.success(request, "Senha alterada com sucesso!")
            return redirect('{}?tab=seguranca'.format(reverse('usuario:perfil')))  # Redirect to perfil view with security tab
        
        # Atualizar informações básicas do perfil
        try:
            perfil.display_name = request.POST.get('display_name', perfil.display_name)
            
            # Processar nome completo (separar em first_name e last_name)
            full_name = request.POST.get('full_name', '').strip()
            if full_name:
                name_parts = full_name.split(' ', 1)
                perfil.first_name = name_parts[0]
                perfil.last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            perfil.phone = request.POST.get('phone', perfil.phone)
            
            # Processar data de nascimento
            birth_date_str = request.POST.get('birth_date', '')
            if birth_date_str:
                try:
                    from datetime import datetime
                    perfil.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                except ValueError:
                    messages.error(request, "Formato de data inválido! Use AAAA-MM-DD.")
                    return redirect('usuario:perfil')
            else:
                perfil.birth_date = None
                
            perfil.gender = request.POST.get('gender', perfil.gender)
            
            perfil.save()
            messages.success(request, "Perfil atualizado com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar o perfil: {str(e)}")
        
        return redirect('usuario:perfil')
    
    # GET: Preparar dados para exibição
    
    # Buscar endereços do usuário
    enderecos = perfil.enderecos.all()
    
    # Buscar pedidos do usuário (otimizado com prefetch)
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-criado_em').prefetch_related('itens__produto')
    
    # Montar contexto base
    context = {
        'perfil': perfil,
        'pedidos': pedidos,
        'enderecos': enderecos
    }
    
    # Adicionar dados administrativos se usuário for superuser
    if request.user.is_superuser:
        context['marcas'] = Marca.objects.all()
        context['categorias'] = Categoria.objects.all()
        context['produtos'] = Produto.objects.all().order_by('-criado_em')
    
    return render(request, 'usuarios/perfil.html', context)


@login_required
def perfil_seguranca(request):
    """
    View para gerenciar a segurança do perfil do usuário
    """
    perfil, created = Perfil.objects.get_or_create(user=request.user)  # type: ignore
    
    if request.method == "POST":
        # Alterar senha
        if 'current_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Verificar se a senha atual está correta
            if not request.user.check_password(current_password):
                messages.error(request, "Senha atual incorreta!")
                return redirect('usuario:perfil')  # Redirect to perfil view instead
            
            # Verificar se as novas senhas coincidem
            if new_password != confirm_password:
                messages.error(request, "As novas senhas não coincidem!")
                return redirect('usuario:perfil')  # Redirect to perfil view instead
            
            # Verificar se a nova senha tem pelo menos 8 caracteres
            if len(new_password) < 8:
                messages.error(request, "A nova senha deve ter pelo menos 8 caracteres!")
                return redirect('usuario:perfil')  # Redirect to perfil view instead
            
            # Verificar se a nova senha atende aos requisitos de complexidade
            import re
            if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', new_password):
                messages.error(request, "A nova senha deve conter pelo menos uma letra maiúscula, uma letra minúscula e um número!")
                return redirect('usuario:perfil')  # Redirect to perfil view instead
            
            # Alterar a senha
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Manter o usuário logado
            messages.success(request, "Senha alterada com sucesso!")
            return redirect('{}?tab=seguranca'.format(reverse('usuario:perfil')))  # Redirect to perfil view with security tab
    
    # For GET requests, redirect to the main perfil page
    return redirect('usuario:perfil')


@login_required
def perfil_endereco(request):
    """
    View para gerenciar os endereços do perfil do usuário
    """
    perfil, created = Perfil.objects.get_or_create(user=request.user)  # type: ignore
    enderecos = perfil.enderecos.all()
    
    if request.method == "POST":
        # Adicionar novo endereço
        label = request.POST.get('label')
        recipient_name = request.POST.get('recipient_name')
        street = request.POST.get('street')
        number = request.POST.get('number')
        complement = request.POST.get('complement', '')
        neighborhood = request.POST.get('neighborhood')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        phone_at_address = request.POST.get('phone_at_address', '')
        
        Endereco.objects.create(  # type: ignore
            perfil=perfil,
            label=label,
            recipient_name=recipient_name,
            street=street,
            number=number,
            complement=complement,
            neighborhood=neighborhood,
            city=city,
            state=state,
            postal_code=postal_code,
            phone_at_address=phone_at_address
        )
        
        messages.success(request, "Endereço adicionado com sucesso!")
        return redirect('usuario:perfil_endereco')
    
    return render(request, 'usuarios/perfil_endereco.html', {'perfil': perfil, 'enderecos': enderecos})


@login_required
def pedido_detalhe(request, pedido_id):
    """
    View para exibir detalhes de um pedido específico
    
    Args:
        request: HttpRequest object (usuário autenticado)
        pedido_id: ID do pedido a ser exibido
            
    Returns:
        Renderiza template 'usuarios/pedido_detalhe.html' com:
        - pedido: Objeto Pedido solicitado (se pertencer ao usuário)
        - itens: Itens do pedido
        
    Raises:
        Http404: Se o pedido não existir ou não pertencer ao usuário
    """
    # Obter o pedido (verifica que pertence ao usuário atual)
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    # Obter itens do pedido
    itens = pedido.itens.all()
    
    return render(request, 'usuarios/pedido_detalhe.html', {
        'pedido': pedido,
        'itens': itens
    })


@login_required
def perfil_preferencias(request):
    """
    View para gerenciar as preferências do perfil do usuário
    """
    perfil, created = Perfil.objects.get_or_create(user=request.user)  # type: ignore
    
    if request.method == "POST":
        # Atualizar preferências
        perfil.newsletter_subscribed = request.POST.get('newsletter_subscribed') == 'on'
        perfil.marketing_opt_in = request.POST.get('marketing_opt_in') == 'on'
        perfil.language = request.POST.get('language', perfil.language)
        perfil.currency = request.POST.get('currency', perfil.currency)
        perfil.display_prices_with_tax = request.POST.get('display_prices_with_tax') == 'on'
        perfil.receive_back_in_stock_alerts = request.POST.get('receive_back_in_stock_alerts') == 'on'
        perfil.preferred_display_style = request.POST.get('preferred_display_style', perfil.preferred_display_style)
        
        perfil.save()
        messages.success(request, "Preferências atualizadas com sucesso!")
        return redirect('usuario:perfil_preferencias')
    
    return render(request, 'usuarios/perfil_preferencias.html', {'perfil': perfil})


@login_required
def perfil_privacidade(request):
    """
    View para gerenciar a privacidade do perfil do usuário
    """
    perfil, created = Perfil.objects.get_or_create(user=request.user)  # type: ignore
    
    if request.method == "POST":
        # Atualizar configurações de privacidade
        perfil.profile_visibility = request.POST.get('profile_visibility', perfil.profile_visibility)
        perfil.show_order_history_public = request.POST.get('show_order_history_public') == 'on'
        
        perfil.save()
        messages.success(request, "Configurações de privacidade atualizadas com sucesso!")
        return redirect('usuario:perfil_privacidade')
    
    return render(request, 'usuarios/perfil_privacidade.html', {'perfil': perfil})


@login_required
def perfil_conta(request):
    """
    View para gerenciar a conta do usuário
    """
    perfil, created = Perfil.objects.get_or_create(user=request.user)  # type: ignore
    
    if request.method == "POST":
        # Verificar se é uma requisição de desativação de conta
        if 'deactivate_account' in request.POST:
            # Lógica para desativar conta
            messages.success(request, "Conta desativada temporariamente!")
            return redirect('usuario:perfil_conta')
        
        # Verificar se é uma requisição de exclusão de conta
        if 'delete_account' in request.POST:
            # Lógica para excluir conta
            messages.success(request, "Conta excluída com sucesso!")
            return redirect('nucleo:index')
    
    return render(request, 'usuarios/perfil_conta.html', {'perfil': perfil})


@login_required
def enderecos(request):
    """
    View para gerenciar endereços do usuário
    """
    # Get or create profile for users who don't have one
    perfil, created = Perfil.objects.get_or_create(user=request.user)  # type: ignore
    enderecos = perfil.enderecos.all()
    
    if request.method == "POST":
        # Adicionar novo endereço
        label = request.POST.get('label')
        recipient_name = request.POST.get('recipient_name')
        street = request.POST.get('street')
        number = request.POST.get('number')
        complement = request.POST.get('complement', '')
        neighborhood = request.POST.get('neighborhood')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        phone_at_address = request.POST.get('phone_at_address', '')
        
        Endereco.objects.create(  # type: ignore
            perfil=perfil,
            label=label,
            recipient_name=recipient_name,
            street=street,
            number=number,
            complement=complement,
            neighborhood=neighborhood,
            city=city,
            state=state,
            postal_code=postal_code,
            phone_at_address=phone_at_address
        )
        
        messages.success(request, "Endereço adicionado com sucesso!")
        return redirect('usuario:enderecos')
    
    return render(request, 'usuarios/enderecos.html', {'enderecos': enderecos})


@login_required
def endereco_editar(request, endereco_id):
    """
    View para editar um endereço específico
    """
    # Get or create profile for users who don't have one
    perfil, created = Perfil.objects.get_or_create(user=request.user)  # type: ignore
    endereco = get_object_or_404(Endereco, id=endereco_id, perfil=perfil)
    
    if request.method == "POST":
        endereco.label = request.POST.get('label', endereco.label)
        endereco.recipient_name = request.POST.get('recipient_name', endereco.recipient_name)
        endereco.street = request.POST.get('street', endereco.street)
        endereco.number = request.POST.get('number', endereco.number)
        endereco.complement = request.POST.get('complement', endereco.complement)
        endereco.neighborhood = request.POST.get('neighborhood', endereco.neighborhood)
        endereco.city = request.POST.get('city', endereco.city)
        endereco.state = request.POST.get('state', endereco.state)
        endereco.postal_code = request.POST.get('postal_code', endereco.postal_code)
        endereco.phone_at_address = request.POST.get('phone_at_address', endereco.phone_at_address)
        
        endereco.save()
        messages.success(request, "Endereço atualizado com sucesso!")
        return redirect('usuario:enderecos')
    
    return render(request, 'usuarios/endereco_editar.html', {'endereco': endereco})


@login_required
def endereco_excluir(request, endereco_id):
    """
    View para excluir um endereço
    """
    # Get or create profile for users who don't have one
    perfil, created = Perfil.objects.get_or_create(user=request.user)  # type: ignore
    endereco = get_object_or_404(Endereco, id=endereco_id, perfil=perfil)
    endereco.delete()
    messages.success(request, "Endereço excluído com sucesso!")
    return redirect('usuario:perfil')


@login_required
def upload_avatar(request):
    """
    View para upload de avatar do usuário
    
    Processa o upload de uma imagem de perfil/avatar para o usuário.
    
    Args:
        request: HttpRequest object (POST com arquivo de imagem)
            Campos esperados:
            - avatar: Arquivo de imagem (PNG, JPG, JPEG)
            
    Returns:
        JsonResponse com:
        - success: Boolean indicando sucesso
        - message: Mensagem de sucesso ou erro
        - avatar_url: URL da nova imagem (se sucesso)
        
    Validations:
        - Apenas usuários autenticados
        - Tipo de arquivo (PNG, JPG, JPEG)
        - Tamanho máximo (5MB)
        - Validação de conteúdo MIME
    """
    if request.method == 'DELETE':
        try:
            # Obter perfil do usuário
            perfil = request.user.perfil
            
            # Se já existir um avatar, remover o arquivo
            if perfil.avatar_url:
                # Extrair o caminho do arquivo do avatar_url
                old_avatar_path = perfil.avatar_url.replace(settings.MEDIA_URL, '')
                old_avatar_full_path = os.path.join(settings.MEDIA_ROOT, old_avatar_path)
                if os.path.exists(old_avatar_full_path):
                    os.remove(old_avatar_full_path)
                
                # Limpar o campo avatar_url
                perfil.avatar_url = ''
                perfil.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Avatar removido com sucesso!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Nenhum avatar encontrado para remover.'
                })
        except Perfil.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Perfil não encontrado.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao remover o avatar: {str(e)}'
            })
    
    if request.method == 'POST' and request.FILES.get('avatar'):
        try:
            avatar_file = request.FILES['avatar']
            
            # Validar tipo de arquivo
            valid_extensions = ['.png', '.jpg', '.jpeg']
            file_extension = os.path.splitext(avatar_file.name)[1].lower()
            
            if file_extension not in valid_extensions:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de arquivo inválido. Apenas PNG, JPG e JPEG são permitidos.'
                })
            
            # Validar tamanho do arquivo (máximo 5MB)
            if avatar_file.size > 5 * 1024 * 1024:  # 5MB em bytes
                return JsonResponse({
                    'success': False,
                    'message': 'Arquivo muito grande. O tamanho máximo permitido é 5MB.'
                })
            
            # Validar tipo MIME
            valid_mime_types = ['image/png', 'image/jpeg']
            if avatar_file.content_type not in valid_mime_types:
                return JsonResponse({
                    'success': False,
                    'message': 'Tipo de arquivo inválido. Apenas imagens PNG e JPEG são permitidas.'
                })
            
            # Obter ou criar perfil
            perfil, created = Perfil.objects.get_or_create(user=request.user)
            
            # Se já existir um avatar, remover o arquivo antigo
            if perfil.avatar_url:
                # Extrair o caminho do arquivo do avatar_url
                old_avatar_path = perfil.avatar_url.replace(settings.MEDIA_URL, '')
                old_avatar_full_path = os.path.join(settings.MEDIA_ROOT, old_avatar_path)
                if os.path.exists(old_avatar_full_path):
                    os.remove(old_avatar_full_path)
            
            # Gerar nome único para o arquivo
            filename = f"{uuid.uuid4()}{file_extension}"
            
            # Criar diretório se não existir
            avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
            os.makedirs(avatar_dir, exist_ok=True)
            
            # Abrir e redimensionar a imagem para 200x200
            image = Image.open(avatar_file)
            image = image.resize((200, 200), Image.Resampling.LANCZOS)
            
            # Converter para RGB se for PNG com transparência
            if image.mode in ('RGBA', 'LA', 'P'):
                # Criar fundo branco para PNGs com transparência
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Salvar a imagem redimensionada
            image_io = BytesIO()
            if file_extension == '.png':
                image.save(image_io, format='PNG')
            else:
                image.save(image_io, format='JPEG', quality=85)
            
            # Salvar no disco
            avatar_path = os.path.join(avatar_dir, filename)
            with open(avatar_path, 'wb') as f:
                f.write(image_io.getvalue())
            
            # Atualizar o campo avatar_url no perfil
            perfil.avatar_url = f"{settings.MEDIA_URL}avatars/{filename}"
            perfil.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Avatar atualizado com sucesso!',
                'avatar_url': perfil.avatar_url
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao fazer upload do avatar: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Nenhum arquivo enviado.'
    })


# ============================================
# VIEWS DE GERENCIAMENTO DE ENDEREÇOS
# ============================================

@login_required
def endereco_adicionar(request):
    """
    Adiciona um novo endereço ao perfil do usuário
    
    Processado via formulário modal na página de perfil.
    Aceita apenas requisições POST.
    
    Args:
        request: HttpRequest object (POST com dados do endereço)
            Campos esperados:
            - label: Rótulo do endereço (ex: "Casa", "Trabalho")
            - recipient_name: Nome do destinatário
            - street: Nome da rua
            - number: Número
            - complement: Complemento (opcional)
            - neighborhood: Bairro
            - city: Cidade
            - state: Estado (UF)
            - postal_code: CEP
            - phone_at_address: Telefone (opcional)
            
    Returns:
        Redirect para 'perfil'
        Mensagem: success (endereço adicionado)
    """
    if request.method == 'POST':
        # Obter ou criar perfil
        perfil, created = Perfil.objects.get_or_create(user=request.user)
        
        # Extrair dados do formulário
        label = request.POST.get('label', '')
        recipient_name = request.POST.get('recipient_name', '')
        street = request.POST.get('street', '')
        number = request.POST.get('number', '')
        complement = request.POST.get('complement', '')
        neighborhood = request.POST.get('neighborhood', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        postal_code = request.POST.get('postal_code', '')
        phone_at_address = request.POST.get('phone_at_address', '')
        
        # Criar novo endereço
        Endereco.objects.create(
            perfil=perfil,
            label=label,
            recipient_name=recipient_name,
            street=street,
            number=number,
            complement=complement,
            neighborhood=neighborhood,
            city=city,
            state=state,
            postal_code=postal_code,
            phone_at_address=phone_at_address
        )
        
        messages.success(request, "Endereço adicionado com sucesso!")
        return redirect('usuario:perfil')
    
    return redirect('usuario:perfil')


@login_required
def endereco_atualizar(request, endereco_id):
    """
    Atualiza um endereço existente do usuário
    
    Processado via formulário modal na página de perfil.
    Aceita apenas requisições POST.
    Verifica que o endereço pertence ao usuário atual.
    
    Args:
        request: HttpRequest object (POST com dados atualizados)
            Campos: mesmos de endereco_adicionar
        endereco_id: ID do endereço a ser atualizado
            
    Returns:
        Redirect para 'perfil'
        Mensagem: success (endereço atualizado)
        
    Raises:
        Http404: Se o endereço não existir ou não pertencer ao usuário
    """
    if request.method == 'POST':
        # Obter perfil e endereço (verifica permissão)
        perfil, created = Perfil.objects.get_or_create(user=request.user)
        endereco = get_object_or_404(Endereco, id=endereco_id, perfil=perfil)
        
        # Atualizar todos os campos
        endereco.label = request.POST.get('label', endereco.label)
        endereco.recipient_name = request.POST.get('recipient_name', endereco.recipient_name)
        endereco.street = request.POST.get('street', endereco.street)
        endereco.number = request.POST.get('number', endereco.number)
        endereco.complement = request.POST.get('complement', endereco.complement)
        endereco.neighborhood = request.POST.get('neighborhood', endereco.neighborhood)
        endereco.city = request.POST.get('city', endereco.city)
        endereco.state = request.POST.get('state', endereco.state)
        endereco.postal_code = request.POST.get('postal_code', endereco.postal_code)
        endereco.phone_at_address = request.POST.get('phone_at_address', endereco.phone_at_address)
        
        # Salvar alterações
        endereco.save()
        messages.success(request, "Endereço atualizado com sucesso!")
        return redirect('usuario:perfil')
    
    return redirect('usuario:perfil')


@login_required
def endereco_excluir(request, endereco_id):
    """
    Exclui um endereço do usuário
    
    Verifica que o endereço pertence ao usuário atual antes de excluir.
    
    Args:
        request: HttpRequest object (usuário autenticado)
        endereco_id: ID do endereço a ser excluído
            
    Returns:
        Redirect para 'perfil'
        Mensagem: success (endereço excluído)
        
    Raises:
        Http404: Se o endereço não existir ou não pertencer ao usuário
        
    Aviso:
        Esta ação é irreversível!
    """
    # Obter perfil e endereço (verifica permissão)
    perfil, created = Perfil.objects.get_or_create(user=request.user)  # type: ignore
    endereco = get_object_or_404(Endereco, id=endereco_id, perfil=perfil)
    
    # Deletar endereço
    endereco.delete()
    messages.success(request, "Endereço excluído com sucesso!")
    return redirect('usuario:perfil')


@login_required
def endereco_definir_principal(request, endereco_id):
    """
    Define um endereço como principal (padrão para entrega)
    
    Args:
        request: HttpRequest object (usuário autenticado)
        endereco_id: ID do endereço a ser definido como principal
            
    Returns:
        Redirect para 'perfil'
        Mensagem: success (endereço definido como principal)
        
    Raises:
        Http404: Se o endereço não existir ou não pertencer ao usuário
    """
    # Obter perfil e endereço (verifica permissão)
    perfil, created = Perfil.objects.get_or_create(user=request.user)
    endereco = get_object_or_404(Endereco, id=endereco_id, perfil=perfil)
    
    # Definir todos os endereços como não principais
    Endereco.objects.filter(perfil=perfil).update(is_default_shipping=False)
    
    # Definir o endereço selecionado como principal
    endereco.is_default_shipping = True
    endereco.save()
    
    messages.success(request, "Endereço definido como principal com sucesso!")
    return redirect('usuario:perfil')
