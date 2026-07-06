from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import ProductFilterForm
from .models import Category, Product, Subcategory


def index(request):
    return render(request, 'catalog/index.html')


def product_list(request):
    products = Product.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(brand__icontains=query))
    form = ProductFilterForm(request.GET or None)
    if form.is_valid():
        data = form.cleaned_data
        if data['min_price'] is not None:
            products = products.filter(price__gte=data['min_price'])
        if data['max_price'] is not None:
            products = products.filter(price__lte=data['max_price'])
        if data['brand']:
            products = products.filter(brand=data['brand'])
        if data['color']:
            products = products.filter(color=data['color'])
        if data['size']:
            products = products.filter(size_variant=data['size'])
        if data['subcategory']:
            products = products.filter(subcategory=data['subcategory'])
        if data['in_stock']:
            products = products.filter(stock__gt=0)
    return render(request, 'catalog/product_list.html', {
        'heading': 'Search results' if query else 'All gear',
        'products': products,
        'categories': Category.objects.all(),
        'form': form,
        'query': query,
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


def cart_view(request):
    cart = Cart(request)
    return render(request, 'catalog/cart.html', {'cart': cart})


@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = Cart(request)
    cart.add(product)
    return redirect('catalog:cart')


@require_POST
def cart_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = Cart(request)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    cart.set_quantity(product, quantity)
    return redirect('catalog:cart')


@require_POST
def cart_remove(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = Cart(request)
    cart.remove(product)
    return redirect('catalog:cart')
