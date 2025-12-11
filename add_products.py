import os
import django
import shutil
from pathlib import Path

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Nerdhub.settings')
django.setup()

from nucleo.models import Marca, Categoria, Produto, Estoque
from django.core.files import File
from django.conf import settings

def add_products_from_images():
    # Define the source image directory
    source_dir = Path('imagens_nerd')
    
    # Get or create brands
    marvel, _ = Marca.objects.get_or_create(nome='Marvel')
    disney, _ = Marca.objects.get_or_create(nome='Disney')
    star_wars, _ = Marca.objects.get_or_create(nome='Star Wars')
    playstation, _ = Marca.objects.get_or_create(nome='PlayStation')
    xbox, _ = Marca.objects.get_or_create(nome='Xbox')
    
    # Get or create categories
    funko_pop, _ = Categoria.objects.get_or_create(nome='Funko Pop')
    action_figure, _ = Categoria.objects.get_or_create(nome='Action Figure')
    camisetas, _ = Categoria.objects.get_or_create(nome='Camisetas')
    acessorios, _ = Categoria.objects.get_or_create(nome='Acessórios')
    legos, _ = Categoria.objects.get_or_create(nome='LEGO')
    
    # Products to create with their corresponding images
    products_data = [
        # Disney products
        {
            'nome': 'Funko Pop Deadpool',
            'descricao': 'Funko Pop do personagem Deadpool com detalhes vermelhos e pretos',
            'preco': 99.90,
            'imagem': 'disney/deadpool.png',
            'marca': marvel,
            'categoria': funko_pop
        },
        {
            'nome': 'Funko Pop Capitão América',
            'descricao': 'Funko Pop do Capitão América com escudo icônico',
            'preco': 99.90,
            'imagem': 'disney/cpt_america.png',
            'marca': marvel,
            'categoria': funko_pop
        },
        {
            'nome': 'Funko Pop Homem-Aranha',
            'descricao': 'Funko Pop do Homem-Aranha em pose clássica',
            'preco': 99.90,
            'imagem': 'disney/funko_miranha.png',
            'marca': marvel,
            'categoria': funko_pop
        },
        {
            'nome': 'Funko Pop Wanda Maximoff',
            'descricao': 'Funko Pop da Feiticeira Escarlate com detalhes em vermelho',
            'preco': 99.90,
            'imagem': 'disney/funko_wanda.png',
            'marca': marvel,
            'categoria': funko_pop
        },
        {
            'nome': 'Garrafa Térmica Marvel',
            'descricao': 'Garrafa térmica com tema Marvel para bebidas quentes ou frias',
            'preco': 79.90,
            'imagem': 'disney/garrafa_marvel.png',
            'marca': marvel,
            'categoria': acessorios
        },
        {
            'nome': 'Luminária Thor',
            'descricao': 'Luminária decorativa com tema do Thor e martelo Mjolnir',
            'preco': 129.90,
            'imagem': 'disney/luminaria_thor.png',
            'marca': marvel,
            'categoria': acessorios
        },
        {
            'nome': 'LEGO Avengers',
            'descricao': 'Conjunto LEGO dos Vingadores com minifiguras',
            'preco': 199.90,
            'imagem': 'disney/lego_avengers.png',
            'marca': marvel,
            'categoria': legos
        },
        {
            'nome': 'LEGO Capitão América',
            'descricao': 'Conjunto LEGO do Capitão América com escudo',
            'preco': 149.90,
            'imagem': 'disney/lego_cpt.png',
            'marca': marvel,
            'categoria': legos
        },
        {
            'nome': 'LEGO Eternals',
            'descricao': 'Conjunto LEGO dos Eternos com personagens icônicos',
            'preco': 249.90,
            'imagem': 'disney/lego_eternals.png',
            'marca': marvel,
            'categoria': legos
        },
        {
            'nome': 'Sandália Homem-Aranha',
            'descricao': 'Sandália confortável com tema do Homem-Aranha',
            'preco': 59.90,
            'imagem': 'disney/sandalia_miranha.png',
            'marca': marvel,
            'categoria': acessorios
        },
        
        # Principal products
        {
            'nome': 'Almofada Portal Rick and Morty',
            'descricao': 'Almofada divertida com tema do Portal de Rick and Morty',
            'preco': 69.90,
            'imagem': 'principal/almofada_portal.png',
            'marca': disney,  # Using Disney as placeholder
            'categoria': acessorios
        },
        {
            'nome': 'Controle PlayStation 5',
            'descricao': 'Controle oficial PlayStation 5 DualSense Wireless',
            'preco': 449.90,
            'imagem': 'principal/controle_ps5.png',
            'marca': playstation,
            'categoria': acessorios
        },
        {
            'nome': 'Funko Pop Minecraft',
            'descricao': 'Funko Pop do personagem do jogo Minecraft',
            'preco': 99.90,
            'imagem': 'principal/funko_mine.png',
            'marca': disney,  # Using Disney as placeholder
            'categoria': funko_pop
        },
        {
            'nome': 'Console PlayStation 5',
            'descricao': 'Console PlayStation 5 com leitor de disco',
            'preco': 3499.90,
            'imagem': 'principal/ps5.png',
            'marca': playstation,
            'categoria': action_figure  # Using as placeholder
        },
    ]
    
    # Create products
    created_count = 0
    for product_data in products_data:
        # Check if product already exists
        if Produto.objects.filter(nome=product_data['nome']).exists():
            print(f"Product '{product_data['nome']}' already exists, skipping...")
            continue
            
        # Copy image to media directory
        source_image_path = source_dir / product_data['imagem']
        if not source_image_path.exists():
            print(f"Image not found: {source_image_path}")
            continue
            
        # Create product
        produto = Produto.objects.create(
            nome=product_data['nome'],
            descricao=product_data['descricao'],
            preco=product_data['preco'],
            marca=product_data['marca'],
            categoria=product_data['categoria']
        )
        
        # Copy image to media directory
        destination_dir = Path(settings.MEDIA_ROOT) / 'produtos'
        destination_dir.mkdir(parents=True, exist_ok=True)
        
        destination_path = destination_dir / source_image_path.name
        shutil.copy2(source_image_path, destination_path)
        
        # Associate image with product
        with open(destination_path, 'rb') as f:
            produto.imagem_principal.save(source_image_path.name, File(f), save=True)
        
        # Create stock
        estoque = Estoque.objects.create(
            produto=produto,
            quantidade=10
        )
        
        print(f"Created product: {produto.nome}")
        created_count += 1
    
    print(f"\nSuccessfully created {created_count} products!")

if __name__ == '__main__':
    add_products_from_images()