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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)
    phone = models.CharField(max_length=30, blank=True)
    shipping_address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)

    def __str__(self):
        return self.user.username
