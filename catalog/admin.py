from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Order, OrderItem, Product, Rating, RecentlyViewed, Subcategory, WishlistItem


# prepopulated_fields fills the slug in as you type the name, in the admin
# form only, it has no effect on how Category itself works.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    # Lets root filter the subcategory list down to one category at a time.
    list_filter = ['category']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'subcategory', 'price', 'stock', 'thumbnail']
    list_filter = ['subcategory', 'brand', 'color']
    search_fields = ['name', 'brand']
    # Price and stock can be edited right from the list, no need to open
    # every product just to restock it.
    list_editable = ['price', 'stock']

    def thumbnail(self, product):
        # format_html escapes the inserted url, which keeps script injection
        # out of the admin.
        if product.image:
            return format_html('<img src="{}" style="height: 40px;">', product.image.url)
        return 'No image'
    # Django shows this text as the column header.
    thumbnail.short_description = 'Image'


# extra=0 means no blank spare rows, only the line items an order actually
# has show up underneath it.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'user', 'status', 'total', 'created_at']
    list_filter = ['status']
    search_fields = ['reference_number', 'user__username']
    # Shows each order's line items directly on its admin page.
    inlines = [OrderItemInline]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'stars', 'created_at']
    # Lets root pull up every 1 star rating at a glance, for example.
    list_filter = ['stars']
    search_fields = ['product__name', 'user__username']


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'added_at']
    search_fields = ['product__name', 'user__username']


@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'viewed_at']
    search_fields = ['product__name', 'user__username']
