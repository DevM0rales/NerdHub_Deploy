import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Nerdhub.settings')
django.setup()

from nucleo.models import Marca, Categoria, Produto, Estoque
from django.contrib.auth.models import User

def create_sample_data():
    # Create admin user if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("Superuser 'admin' created with password 'admin'")
    
    # Create sample brands
    marcas_data = [
        {'nome': 'Marvel', 'logo': None},
        {'nome': 'Star Wars', 'logo': None},
        {'nome': 'Disney', 'logo': None},
        {'nome': 'PlayStation', 'logo': None},
        {'nome': 'Xbox', 'logo': None},
    ]
    
    marcas = []
    for marca_data in marcas_data:
        marca, created = Marca.objects.get_or_create(
            nome=marca_data['nome'],
            defaults=marca_data
        )
        marcas.append(marca)
        if created:
            print(f"Created brand: {marca.nome}")
    
    # Create sample categories
    categorias_data = [
        {'nome': 'Funko Pop'},
        {'nome': 'Action Figure'},
        {'nome': 'Camisetas'},
        {'nome': 'Acessórios'},
    ]
    
    categorias = []
    for categoria_data in categorias_data:
        categoria, created = Categoria.objects.get_or_create(
            nome=categoria_data['nome'],
            defaults=categoria_data
        )
        categorias.append(categoria)
        if created:
            print(f"Created category: {categoria.nome}")
    
    # Create sample products
    produtos_data = [
        {
            'nome': 'Funko Pop Spider-Man',
            'descricao': 'Funko Pop do Homem-Aranha em pose clássica',
            'preco': 99.90,
            'imagem_principal': 'produtos/spiderman.jpg',
            'marca': marcas[0],  # Marvel
            'categoria': categorias[0],  # Funko Pop
        },
        {
            'nome': 'Funko Pop Darth Vader',
            'descricao': 'Funko Pop do Darth Vader com detalhes em preto',
            'preco': 89.90,
            'imagem_principal': 'produtos/darthvader.jpg',
            'marca': marcas[1],  # Star Wars
            'categoria': categorias[0],  # Funko Pop
        },
        {
            'nome': 'Camiseta Marvel Avengers',
            'descricao': 'Camiseta oficial dos Vingadores em tamanho único',
            'preco': 79.90,
            'imagem_principal': 'produtos/camiseta_avengers.jpg',
            'marca': marcas[0],  # Marvel
            'categoria': categorias[2],  # Camisetas
        },
        {
            'nome': 'Action Figure Yoda',
            'descricao': 'Action figure do Mestre Yoda com 15cm de altura',
            'preco': 149.90,
            'imagem_principal': 'produtos/yoda.jpg',
            'marca': marcas[1],  # Star Wars
            'categoria': categorias[1],  # Action Figure
        },
    ]
    
    produtos = []
    for produto_data in produtos_data:
        # Check if product already exists
        if not Produto.objects.filter(nome=produto_data['nome']).exists():
            produto = Produto.objects.create(**produto_data)
            produtos.append(produto)
            print(f"Created product: {produto.nome}")
            
            # Create stock for the product
            estoque = Estoque.objects.create(
                produto=produto,
                quantidade=10
            )
            print(f"Created stock for {produto.nome}: {estoque.quantidade} units")
    
    print("Sample data population completed!")

if __name__ == '__main__':
    create_sample_data()