from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Order, OrderItem, Product, Subcategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'subcategory', 'price', 'stock', 'thumbnail']
    list_filter = ['subcategory', 'brand', 'color']
    search_fields = ['name', 'brand']
    list_editable = ['price', 'stock']

    def thumbnail(self, product):
        if product.image:
            return format_html('<img src="{}" style="height: 40px;">', product.image.url)
        return 'No image'
    thumbnail.short_description = 'Image'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'user', 'status', 'total', 'created_at']
    list_filter = ['status']
    search_fields = ['reference_number', 'user__username']
    inlines = [OrderItemInline]
