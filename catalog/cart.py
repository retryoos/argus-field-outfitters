# The cart is a plain dict in the session that maps a product id to a quantity.
# It lives there instead of the database so a guest can fill a cart before
# signing in. Session data is stored as JSON, which is why the keys are strings
from .models import Product

CART_SESSION_KEY = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        # Read only. Nothing is written back until something is actually added,
        # so a visitor who only browses never gets a session row of their own
        self.cart = self.session.get(CART_SESSION_KEY, {})
        self._rows = None

    def add(self, product, quantity=1):
        key = str(product.id)
        self.cart[key] = self.cart.get(key, 0) + quantity
        self.save()

    def set_quantity(self, product, quantity):
        # Setting the quantity to zero removes the item from the cart
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
        self.cart = {}
        self.save()

    def quantity_of(self, product):
        return self.cart.get(str(product.id), 0)

    def save(self):
        self.session[CART_SESSION_KEY] = self.cart
        # Mark the session as changed so Django writes it back
        self.session.modified = True
        self._rows = None

    def rows(self):
        # A product can be deleted from the catalogue while it is still sitting
        # in someone's session, so the cart is read against the products that
        # still exist and any leftover id is dropped. Everything below counts
        # from this one list, which keeps the count, the totals and the lines on
        # the page from ever disagreeing with each other
        if self._rows is None:
            products = list(Product.objects.filter(id__in=self.cart.keys()))
            if len(products) != len(self.cart):
                live = {str(product.id) for product in products}
                self.cart = {k: v for k, v in self.cart.items() if k in live}
                self.session[CART_SESSION_KEY] = self.cart
                self.session.modified = True
            self._rows = [{
                'product': product,
                'quantity': self.cart[str(product.id)],
                'total': product.price * self.cart[str(product.id)],
            } for product in products]
        return self._rows

    def __iter__(self):
        # Yield each row with its product loaded so templates can loop the cart
        return iter(self.rows())

    def __len__(self):
        # Counts every unit in the cart, which is what len and the navbar
        # badge use
        return sum(row['quantity'] for row in self.rows())

    def total_price(self):
        return sum(row['total'] for row in self.rows())
