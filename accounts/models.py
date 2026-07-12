from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    CUSTOMER = 'customer'
    EMPLOYEE = 'employee'
    OWNER = 'owner'
    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (EMPLOYEE, 'Employee'),
        (OWNER, 'Owner'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # The role decides what the user can reach, and new accounts default as customers
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)
    phone = models.CharField(max_length=30, blank=True)
    # These four mirror the shipping fields on Order, so a saved address can
    # prefill every field on the checkout form
    shipping_address = models.TextField(blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_postcode = models.CharField(max_length=5, blank=True)
    shipping_country = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)

    def __str__(self):
        return self.user.username

    # Small helper funcs so templates can check roles without repeating the strings
    @property
    def is_owner(self):
        return self.role == self.OWNER

    @property
    def is_staff_member(self):
        return self.role in (self.EMPLOYEE, self.OWNER)
