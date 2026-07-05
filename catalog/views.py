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


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    same_subcategory = Product.objects.filter(
        subcategory=product.subcategory, stock__gt=0
    ).exclude(pk=product.pk).order_by('-created_at')
    if same_subcategory.count() >= 4:
        related = same_subcategory[:4]
    else:
        related = Product.objects.filter(
            subcategory__category=product.subcategory.category, stock__gt=0
        ).exclude(pk=product.pk).order_by('-created_at')[:4]
    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'related_products': related,
    })
