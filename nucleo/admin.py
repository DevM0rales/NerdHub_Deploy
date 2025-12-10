from django.contrib import admin
from .models import Produto, ImagemProduto, Marca, Categoria

class ImagemProdutoInline(admin.TabularInline):
    model = ImagemProduto
    extra = 1

class ProdutoAdmin(admin.ModelAdmin):
    inlines = [ImagemProdutoInline]

admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Marca)
admin.site.register(Categoria)
