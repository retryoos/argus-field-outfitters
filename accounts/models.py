from django.contrib.auth.models import User
from django.db import models

from .roles import role_of


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=30, blank=True)
    # These four mirror the shipping fields on Order, so a saved address can
    # prefill every field on the checkout form
    shipping_address = models.TextField(blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_postcode = models.CharField(max_length=5, blank=True)
    shipping_country = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)

    class Meta:
        # The two gates the backoffice checks. These are hung on Profile because
        # it is the accounts app's own model, but they are not about one profile,
        # they are what the Employee and Owner groups grant. access_backoffice
        # goes to both groups, manage_users only to Owner.
        permissions = [
            ('access_backoffice', 'Can access the backoffice'),
            ('manage_users', 'Can manage user roles'),
        ]

    def __str__(self):
        return self.user.username

    @property
    def role_label(self):
        # What the profile and dashboard pages display, read from the user's
        # group membership rather than a stored field.
        return role_of(self.user)
