# The staff panels. Everything here sits behind a role check, staff_required
# for the catalogue and the orders and owner_required for user management.
from django.contrib.auth.models import User
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import UserRoleForm
from accounts.models import Profile
from catalog.forms import CategoryForm, ProductForm, SubcategoryForm
from catalog.models import Category, Order, Product, Subcategory

from .permissions import owner_required, staff_required

# Only these keys are ever passed to order_by, so a query string can never
# sort by an arbitrary field name.
PRODUCT_SORT_FIELDS = {
    'name': 'name', '-name': '-name',
    'price': 'price', '-price': '-price',
    'stock': 'stock', '-stock': '-stock',
}

ORDER_SORT_FIELDS = {
    'date': 'created_at', '-date': '-created_at',
    'status': 'status', '-status': '-status',
    'total': 'total', '-total': '-total',
}


@staff_required
def panel_home(request):
    counts = {
        'products': Product.objects.count(),
        'categories': Category.objects.count(),
        'subcategories': Subcategory.objects.count(),
        'orders': Order.objects.count(),
    }
    return render(request, 'backoffice/panel_home.html', {'counts': counts})


@staff_required
def product_list(request):
    # select_related fetches the subcategory in the same query instead of
    # one extra query per row.
    products = Product.objects.select_related('subcategory')
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(brand__icontains=query))
    sort = request.GET.get('sort', 'name')
    products = products.order_by(PRODUCT_SORT_FIELDS.get(sort, 'name'))
    return render(request, 'backoffice/product_list.html', {
        'products': products,
        'query': query,
        'sort': sort,
    })


@staff_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('backoffice:product_list')
    else:
        form = ProductForm()
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Add product',
        'cancel_url': 'backoffice:product_list',
    })


@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('backoffice:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Edit product',
        'cancel_url': 'backoffice:product_list',
    })


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    error = ''
    if request.method == 'POST':
        # Products inside past orders are protected from deletion.
        try:
            product.delete()
            return redirect('backoffice:product_list')
        except ProtectedError:
            error = 'This product is part of past orders so it cannot be deleted.'
    return render(request, 'backoffice/confirm_delete.html', {
        'object': product,
        'cancel_url': 'backoffice:product_list',
        'error': error,
    })


@staff_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'backoffice/category_list.html', {'categories': categories})


@staff_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('backoffice:category_list')
    else:
        form = CategoryForm()
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Add category',
        'cancel_url': 'backoffice:category_list',
    })


@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('backoffice:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Edit category',
        'cancel_url': 'backoffice:category_list',
    })


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    error = ''
    if request.method == 'POST':
        # A category cannot go away while products still live under it.
        try:
            category.delete()
            return redirect('backoffice:category_list')
        except ProtectedError:
            error = 'This category still contains products so it cannot be deleted.'
    return render(request, 'backoffice/confirm_delete.html', {
        'object': category,
        'cancel_url': 'backoffice:category_list',
        'error': error,
    })


@staff_required
def subcategory_list(request):
    subcategories = Subcategory.objects.select_related('category')
    return render(request, 'backoffice/subcategory_list.html', {'subcategories': subcategories})


@staff_required
def subcategory_create(request):
    if request.method == 'POST':
        form = SubcategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('backoffice:subcategory_list')
    else:
        form = SubcategoryForm()
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Add subcategory',
        'cancel_url': 'backoffice:subcategory_list',
    })


@staff_required
def subcategory_edit(request, pk):
    subcategory = get_object_or_404(Subcategory, pk=pk)
    if request.method == 'POST':
        form = SubcategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            return redirect('backoffice:subcategory_list')
    else:
        form = SubcategoryForm(instance=subcategory)
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': 'Edit subcategory',
        'cancel_url': 'backoffice:subcategory_list',
    })


@staff_required
def subcategory_delete(request, pk):
    subcategory = get_object_or_404(Subcategory, pk=pk)
    error = ''
    if request.method == 'POST':
        # A subcategory with products is protected from deletion.
        try:
            subcategory.delete()
            return redirect('backoffice:subcategory_list')
        except ProtectedError:
            error = 'This subcategory still has products in it so it cannot be deleted.'
    return render(request, 'backoffice/confirm_delete.html', {
        'object': subcategory,
        'cancel_url': 'backoffice:subcategory_list',
        'error': error,
    })


@staff_required
def order_list(request):
    orders = Order.objects.select_related('user')
    query = request.GET.get('q', '').strip()
    if query:
        orders = orders.filter(Q(reference_number__icontains=query) | Q(user__username__icontains=query))
    sort = request.GET.get('sort', '-date')
    orders = orders.order_by(ORDER_SORT_FIELDS.get(sort, '-created_at'))
    return render(request, 'backoffice/order_list.html', {
        'orders': orders,
        'query': query,
        'sort': sort,
    })


@staff_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'backoffice/order_detail.html', {'order': order})


@owner_required
def user_list(request):
    users = User.objects.select_related('profile').order_by('username')
    return render(request, 'backoffice/user_list.html', {'users': users})


@owner_required
def user_role_edit(request, pk):
    account = get_object_or_404(User, pk=pk)
    profile, created = Profile.objects.get_or_create(user=account)
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('backoffice:user_list')
    else:
        form = UserRoleForm(instance=profile)
    return render(request, 'backoffice/form.html', {
        'form': form,
        'title': f'Set role for {account.username}',
        'cancel_url': 'backoffice:user_list',
    })
