from .models import Product

CART_SESSION_KEY = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        key = str(product.id)
        self.cart[key] = self.cart.get(key, 0) + quantity
        self.save()

    def set_quantity(self, product, quantity):
        key = str(product.id)
        if quantity > 0:
            self.cart[key] = quantity
            self.save()
        else:
            self.remove(product)

    def remove(self, product):
        key = str(product.id)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        products = Product.objects.filter(id__in=self.cart.keys())
        for product in products:
            quantity = self.cart[str(product.id)]
            yield {
                'product': product,
                'quantity': quantity,
                'total': product.price * quantity,
            }

    def __len__(self):
        return sum(self.cart.values())

    def total_price(self):
        products = Product.objects.filter(id__in=self.cart.keys())
        return sum(product.price * self.cart[str(product.id)] for product in products)
