from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'subcategories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    # PROTECT stops a subcategory from being deleted while products still use it.
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='products')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    size_variant = models.CharField(max_length=50, blank=True, default='One Size')
    color = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Order(models.Model):
    PENDING = 'pending'
    PAID = 'paid'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    reference_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ship_full_name = models.CharField(max_length=200)
    ship_address = models.TextField()
    ship_city = models.CharField(max_length=100)
    ship_postcode = models.CharField(max_length=20)
    ship_country = models.CharField(max_length=100)
    billing_same = models.BooleanField(default=True)
    stripe_session_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.reference_number or f'Order {self.pk}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # PROTECT keeps a product from disappearing out of past orders.
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    # Keeps the price that was paid so a later price change does not rewrite
    # old orders.
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def subtotal(self):
        return self.unit_price * self.quantity


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    stars = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Each user can rate a product once.
        unique_together = [['user', 'product']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.stars} stars for {self.product.name}'


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'product']]
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.product.name} for {self.user.username}'


class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recently_viewed')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='viewed_by')
    # auto_now bumps the timestamp on every save, so opening a product again
    # moves it back to the top of the list.
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'product']]
        ordering = ['-viewed_at']

    def __str__(self):
        return f'{self.user.username} viewed {self.product.name}'
