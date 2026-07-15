from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('subcategory/<slug:slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:pk>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
    # Stripe posts here itself, no shopper ever opens this url
    path('checkout/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('order/<int:pk>/', views.order_confirmation, name='order_confirmation'),
    path('rate/<int:pk>/', views.rate, name='rate'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/toggle/<int:pk>/', views.wishlist_toggle, name='wishlist_toggle'),
]
