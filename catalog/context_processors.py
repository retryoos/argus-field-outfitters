from .cart import Cart


# Makes the cart item count available to every template so the navbar badge
# can show it on any page
def cart_count(request):
    return {'cart_count': len(Cart(request))}
