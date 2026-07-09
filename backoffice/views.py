from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import UserRoleForm
from accounts.models import Profile
from catalog.forms import CategoryForm, ProductForm, SubcategoryForm
from catalog.models import Category, Order, Product, Subcategory


@login_required
def panel_home(request):
    counts = {
        'products': Product.objects.count(),
        'categories': Category.objects.count(),
        'subcategories': Subcategory.objects.count(),
        'orders': Order.objects.count(),
    }
    return render(request, 'backoffice/panel_home.html', {'counts': counts})


@login_required
def product_list(request):
    products = Product.objects.select_related('subcategory')
    return render(request, 'backoffice/product_list.html', {'products': products})


@login_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('backoffice:product_list')
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Add product',
        'cancel_url': 'backoffice:product_list',
    })


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('backoffice:product_list')
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Edit product',
        'cancel_url': 'backoffice:product_list',
    })


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('backoffice:product_list')
    return render(request, 'backoffice/confirm_delete.html', {
        'object': product,
        'cancel_url': 'backoffice:product_list',
    })


@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'backoffice/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('backoffice:category_list')
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Add category',
        'cancel_url': 'backoffice:category_list',
    })


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('backoffice:category_list')
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Edit category',
        'cancel_url': 'backoffice:category_list',
    })


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('backoffice:category_list')
    return render(request, 'backoffice/confirm_delete.html', {
        'object': category,
        'cancel_url': 'backoffice:category_list',
    })


@login_required
def subcategory_list(request):
    subcategories = Subcategory.objects.select_related('category')
    return render(request, 'backoffice/subcategory_list.html', {'subcategories': subcategories})


@login_required
def subcategory_create(request):
    form = SubcategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('backoffice:subcategory_list')
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Add subcategory',
        'cancel_url': 'backoffice:subcategory_list',
    })


@login_required
def subcategory_edit(request, pk):
    subcategory = get_object_or_404(Subcategory, pk=pk)
    form = SubcategoryForm(request.POST or None, instance=subcategory)
    if form.is_valid():
        form.save()
        return redirect('backoffice:subcategory_list')
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Edit subcategory',
        'cancel_url': 'backoffice:subcategory_list',
    })


@login_required
def subcategory_delete(request, pk):
    subcategory = get_object_or_404(Subcategory, pk=pk)
    if request.method == 'POST':
        subcategory.delete()
        return redirect('backoffice:subcategory_list')
    return render(request, 'backoffice/confirm_delete.html', {
        'object': subcategory,
        'cancel_url': 'backoffice:subcategory_list',
    })


@login_required
def order_list(request):
    orders = Order.objects.select_related('user')
    return render(request, 'backoffice/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'backoffice/order_detail.html', {'order': order})


@login_required
def user_list(request):
    users = User.objects.select_related('profile').order_by('username')
    return render(request, 'backoffice/user_list.html', {'users': users})


@login_required
def user_role_edit(request, pk):
    account = get_object_or_404(User, pk=pk)
    profile, created = Profile.objects.get_or_create(user=account)
    form = UserRoleForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('backoffice:user_list')
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Set role for ' + account.username,
        'cancel_url': 'backoffice:user_list',
    })
