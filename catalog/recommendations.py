from .models import Product, RecentlyViewed


# Suggest products from the same subcategory as the last item the user opened,
# skipping anything they have already seen. A user with no history gets the
# newest gear instead so the block is never empty
def recommendations_for_user(user, limit=4):
    recent = RecentlyViewed.objects.filter(user=user).select_related('product').first()
    if recent:
        viewed_ids = RecentlyViewed.objects.filter(user=user).values_list('product_id', flat=True)
        suggestions = (Product.objects
                       .filter(subcategory=recent.product.subcategory, stock__gt=0)
                       .exclude(id__in=viewed_ids)
                       .order_by('-created_at')[:limit])
        if suggestions:
            return suggestions
    return Product.objects.filter(stock__gt=0).order_by('-created_at')[:limit]
