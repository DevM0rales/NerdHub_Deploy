#!/usr/bin/env python
"""
Script para adicionar produtos automaticamente usando as imagens da pasta imagens_nerd
"""

import os
import sys
import django
from pathlib import Path

# Configurar o ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Nerdhub.settings')
django.setup()

from django.core.files import File
from django.conf import settings
from nucleo.models import Produto, Marca, Categoria
from shutil import copy2

def get_or_create_brand(name):
    """Obtém ou cria uma marca"""
    brand, created = Marca.objects.get_or_create(
        nome__iexact=name,
        defaults={'nome': name.capitalize()}
    )
    if created:
        print(f"Criada nova marca: {brand.nome}")
    return brand

def get_or_create_category(name):
    """Obtém ou cria uma categoria"""
    category, created = Categoria.objects.get_or_create(
        nome__iexact=name,
        defaults={'nome': name.capitalize()}
    )
    if created:
        print(f"Criada nova categoria: {category.nome}")
    return category

def create_product_from_image(image_path, brand, category):
    """Cria um produto a partir de uma imagem"""
    # Extrair nome do arquivo sem extensão
    filename = os.path.basename(image_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    # Criar um nome amigável para o produto
    product_name = name_without_ext.replace('_', ' ').replace('-', ' ')
    product_name = ' '.join(word.capitalize() for word in product_name.split())
    
    # Verificar se o produto já existe
    if Produto.objects.filter(nome__iexact=product_name).exists():
        print(f"Produto '{product_name}' já existe, pulando...")
        return None
    
    # Determinar preço baseado no tipo de produto
    price = 149.90  # Preço padrão
    if 'lego' in product_name.lower():
        price = 199.90
    elif 'controle' in product_name.lower() or 'fone' in product_name.lower():
        price = 299.90
    elif 'jogo' in product_name.lower() or 'game' in product_name.lower():
        price = 249.90
    elif 'almofada' in product_name.lower() or 'pantufa' in product_name.lower():
        price = 89.90
    elif 'luminaria' in product_name.lower():
        price = 129.90
    
    # Copiar imagem para o diretório de mídia
    media_root = settings.MEDIA_ROOT
    destination_dir = os.path.join(media_root, 'produtos')
    os.makedirs(destination_dir, exist_ok=True)
    
    destination_path = os.path.join(destination_dir, filename)
    copy2(image_path, destination_path)
    
    # Criar produto
    product = Produto.objects.create(
        nome=product_name,
        descricao=f"Produto oficial {product_name} de excelente qualidade.",
        preco=price,
        imagem_principal=f'produtos/{filename}',
        marca=brand,
        categoria=category
    )
    
    print(f"Criado produto: {product.nome} - R$ {product.preco}")
    return product

def main():
    """Função principal para adicionar produtos"""
    print("Iniciando processo de adição de produtos...")
    
    # Definir caminho base
    base_path = Path("imagens_nerd")
    
    # Disney products
    disney_path = base_path / "disney"
    if disney_path.exists():
        print("\nProcessando produtos Disney...")
        disney_brand = get_or_create_brand("Disney")
        funko_category = get_or_create_category("Funko Pop")
        
        for image_file in disney_path.iterdir():
            if image_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                create_product_from_image(str(image_file), disney_brand, funko_category)
    
    # Principal products
    principal_path = base_path / "principal"
    if principal_path.exists():
        print("\nProcessando produtos principais...")
        generic_brand = get_or_create_brand("Genérica")
        accessories_category = get_or_create_category("Acessórios")
        
        for image_file in principal_path.iterdir():
            if image_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                # Determinar categoria baseada no nome do arquivo
                filename = image_file.name.lower()
                if 'almofada' in filename or 'luminaria' in filename:
                    category = get_or_create_category("Acessórios")
                elif 'lego' in filename:
                    category = get_or_create_category("LEGO")
                elif 'funko' in filename or 'pop' in filename:
                    category = get_or_create_category("Funko Pop")
                elif 'ps5' in filename or 'controle' in filename:
                    category = get_or_create_category("Acessórios")
                else:
                    category = accessories_category
                    
                create_product_from_image(str(image_file), generic_brand, category)
    
    # Star Wars products
    starwars_path = base_path / "starwars" / "starwars"
    if starwars_path.exists():
        print("\nProcessando produtos Star Wars...")
        starwars_brand = get_or_create_brand("Star Wars")
        funko_category = get_or_create_category("Funko Pop")
        
        for image_file in starwars_path.iterdir():
            if image_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                create_product_from_image(str(image_file), starwars_brand, funko_category)
    
    # Xbox products
    xbox_path = base_path / "xbox" / "xbox"
    if xbox_path.exists():
        print("\nProcessando produtos Xbox...")
        xbox_brand = get_or_create_brand("Xbox")
        accessories_category = get_or_create_category("Acessórios")
        funko_category = get_or_create_category("Funko Pop")
        
        for image_file in xbox_path.iterdir():
            if image_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                # Determinar categoria baseada no nome do arquivo
                filename = image_file.name.lower()
                if 'funko' in filename:
                    category = funko_category
                elif 'jogo' in filename:
                    category = get_or_create_category("Jogos")
                else:
                    category = accessories_category
                    
                create_product_from_image(str(image_file), xbox_brand, category)
    
    print("\nProcesso concluído! Produtos adicionados com sucesso.")

if __name__ == "__main__":
    main()