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
]
