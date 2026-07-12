import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import Profile

from .cart import Cart
from .forms import CartUpdateForm, CheckoutForm, ProductFilterForm, RatingForm
from .models import Category, Order, OrderItem, Product, Rating, RecentlyViewed, Subcategory, WishlistItem


def index(request):
    return render(request, 'catalog/index.html', {
        'new_arrivals': Product.objects.filter(stock__gt=0).annotate(
            average_rating=Avg('ratings__stars')
        ).order_by('-created_at')[:4],
        'categories': Category.objects.all(),
    })


def product_list(request):
    # The annotation puts each product's average star rating on the card
    # grid, one query for the whole page instead of one per card.
    products = Product.objects.annotate(average_rating=Avg('ratings__stars'))
    # The search box matches the product name or the brand. Q objects let
    # the two checks combine with OR in a single query.
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(brand__icontains=query))
    # The filters narrow down whatever the search left, so both work together.
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
    products = Product.objects.filter(subcategory__category=category).annotate(average_rating=Avg('ratings__stars'))
    return render(request, 'catalog/product_list.html', {
        'heading': category.name,
        'products': products,
        'categories': Category.objects.all(),
    })


def subcategory_detail(request, slug):
    subcategory = get_object_or_404(Subcategory, slug=slug)
    products = Product.objects.filter(subcategory=subcategory).annotate(average_rating=Avg('ratings__stars'))
    return render(request, 'catalog/product_list.html', {
        'heading': subcategory.name,
        'products': products,
        'categories': Category.objects.all(),
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Remember the visit so the dashboard and the recommender can use it.
    if request.user.is_authenticated:
        RecentlyViewed.objects.update_or_create(user=request.user, product=product)
    # Related items come from the same subcategory. When that has fewer than
    # four to offer, the wider category is used instead.
    same_subcategory = Product.objects.filter(
        subcategory=product.subcategory, stock__gt=0
    ).exclude(pk=product.pk).order_by('-created_at')
    if same_subcategory.count() >= 4:
        related = same_subcategory[:4]
    else:
        related = Product.objects.filter(
            subcategory__category=product.subcategory.category, stock__gt=0
        ).exclude(pk=product.pk).order_by('-created_at')[:4]
    reviews = product.ratings.select_related('user')
    average = product.ratings.aggregate(average=Avg('stars'))['average']
    in_wishlist = (
        request.user.is_authenticated
        and WishlistItem.objects.filter(user=request.user, product=product).exists()
    )
    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'related_products': related,
        'reviews': reviews,
        'average': round(average, 1) if average is not None else 0,
        'rating_count': reviews.count(),
        'in_wishlist': in_wishlist,
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


def _checkout_initial(user):
    # Prefill the shipping form with whatever the profile already knows.
    # hasattr covers accounts that never got a profile row.
    initial = {'ship_full_name': user.get_full_name()}
    if hasattr(user, 'profile'):
        profile = user.profile
        initial['ship_address'] = profile.shipping_address
        initial['ship_city'] = profile.shipping_city
        initial['ship_postcode'] = profile.shipping_postcode
        initial['ship_country'] = profile.shipping_country
    return initial


def _save_address(user, data):
    # Only runs when the shopper ticks "save this address". get_or_create
    # covers a brand new customer who has never visited their profile page,
    # and so has no Profile row yet.
    profile, created = Profile.objects.get_or_create(user=user)
    profile.shipping_address = data['ship_address']
    profile.shipping_city = data['ship_city']
    profile.shipping_postcode = data['ship_postcode']
    profile.shipping_country = data['ship_country']
    profile.save()


def _create_order(request, cart, data):
    order = Order.objects.create(
        user=request.user,
        ship_full_name=data['ship_full_name'],
        ship_address=data['ship_address'],
        ship_city=data['ship_city'],
        ship_postcode=data['ship_postcode'],
        ship_country=data['ship_country'],
        total=cart.total_price(),
    )
    # The reference is built from the primary key so it is unique for free,
    # padded to six digits so it reads like a real order number.
    order.reference_number = f'AFO-{order.pk:06d}'
    order.save()
    for item in cart:
        # The price is copied onto the order line so old orders keep the
        # price that was actually paid.
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            unit_price=item['product'].price,
        )
    return order


def _finalize_order(order):
    # Marking an order paid also takes the bought quantities out of stock.
    order.status = Order.PAID
    order.paid_at = timezone.now()
    order.save()
    for item in order.items.all():
        product = item.product
        # max keeps stock from going below zero.
        product.stock = max(product.stock - item.quantity, 0)
        product.save()


def _stripe_enabled():
    # Without Stripe keys the checkout skips the payment page and completes
    # at once. That keeps local development simple.
    return bool(settings.STRIPE_SECRET_KEY)


def _start_stripe_session(request, order):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    line_items = []
    for item in order.items.all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': item.product.name},
                # Stripe wants amounts in cents.
                'unit_amount': int(item.unit_price * 100),
            },
            'quantity': item.quantity,
        })
    # This is the standard checkout session flow from the Stripe docs.
    # build_absolute_uri produces full addresses with the domain, which
    # Stripe needs because it redirects from its own site. The braces in the
    # success url are literal text that Stripe fills in with the session id,
    # not Python formatting.
    success_url = request.build_absolute_uri(reverse('catalog:checkout_success'))
    session = stripe.checkout.Session.create(
        mode='payment',
        line_items=line_items,
        success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('catalog:checkout_cancel')),
    )
    order.stripe_session_id = session.id
    order.save()
    return session.url


@login_required
def checkout(request):
    cart = Cart(request)
    # There is nothing to check out when the cart is empty.
    if len(cart) == 0:
        return redirect('catalog:cart')
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['save_address']:
                _save_address(request.user, form.cleaned_data)
            order = _create_order(request, cart, form.cleaned_data)
            if _stripe_enabled():
                return redirect(_start_stripe_session(request, order))
            _finalize_order(order)
            cart.clear()
            return redirect('catalog:order_confirmation', pk=order.pk)
    else:
        form = CheckoutForm(initial=_checkout_initial(request.user))
    return render(request, 'catalog/checkout.html', {
        'form': form,
        'cart': cart,
        'stripe_enabled': _stripe_enabled(),
    })


@login_required
def checkout_success(request):
    # Stripe sends the shopper here after payment. The order is marked paid
    # only after Stripe confirms the session, and the status check stops a
    # page refresh from processing the same order twice.
    session_id = request.GET.get('session_id')
    order = get_object_or_404(Order, stripe_session_id=session_id, user=request.user)
    if order.status != Order.PAID:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            _finalize_order(order)
            Cart(request).clear()
    return redirect('catalog:order_confirmation', pk=order.pk)


@login_required
def checkout_cancel(request):
    return redirect('catalog:cart')


@login_required
def order_confirmation(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'catalog/order_confirmation.html', {'order': order})


@login_required
@require_POST
def rate(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = RatingForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'invalid rating'}, status=400)
    # Each user gets one rating per product. Rating again replaces the old one.
    Rating.objects.update_or_create(
        user=request.user,
        product=product,
        defaults={
            'stars': form.cleaned_data['stars'],
            'comment': form.cleaned_data['comment'],
        },
    )
    average = product.ratings.aggregate(average=Avg('stars'))['average']
    return JsonResponse({
        'average': round(average, 1) if average is not None else 0,
        'count': product.ratings.count(),
    })


@login_required
def wishlist(request):
    items = request.user.wishlist_items.select_related('product')
    return render(request, 'catalog/wishlist.html', {'items': items})


@login_required
@require_POST
def wishlist_toggle(request, pk):
    # The same button adds and removes, which keeps the template simple.
    product = get_object_or_404(Product, pk=pk)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
    # Only follow next targets that point somewhere inside the site. A value
    # starting with two slashes would point at another host, so it is refused.
    next_url = request.POST.get('next', '')
    if not next_url.startswith('/') or next_url.startswith('//'):
        next_url = ''
    return redirect(next_url or 'catalog:wishlist')
