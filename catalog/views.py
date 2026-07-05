from django.shortcuts import get_object_or_404, render

from .models import Category, Product, Subcategory


def index(request):
    return render(request, 'catalog/index.html')


def product_list(request):
    products = Product.objects.all()
    return render(request, 'catalog/product_list.html', {
        'heading': 'All gear',
        'products': products,
        'categories': Category.objects.all(),
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(subcategory__category=category)
    return render(request, 'catalog/product_list.html', {
        'heading': category.name,
        'products': products,
        'categories': Category.objects.all(),
    })


def subcategory_detail(request, slug):
    subcategory = get_object_or_404(Subcategory, slug=slug)
    products = Product.objects.filter(subcategory=subcategory)
    return render(request, 'catalog/product_list.html', {
        'heading': subcategory.name,
        'products': products,
        'categories': Category.objects.all(),
    })
