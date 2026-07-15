from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from catalog.forms import COUNTRY_CHOICES, postcode_validator

from .models import Profile
from .roles import EMPLOYEE, OWNER


# The built in form only asks for a username and pw, this one adds the
# email and the name so the profile page has something to show
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):
    # Overridden so the profile edit page offers the same country dropdown
    # and postcode rule as checkout, instead of the model's plain text field.
    shipping_country = forms.ChoiceField(choices=[('', 'Not set')] + COUNTRY_CHOICES, required=False)
    shipping_postcode = forms.CharField(max_length=10, required=False, validators=[postcode_validator])

    class Meta:
        model = Profile
        fields = ['phone', 'shipping_address', 'shipping_city', 'shipping_postcode', 'shipping_country', 'avatar']


# The owner picks one of these three on the set role screen. Customer is the
# no-group option, the other two match the Employee and Owner group names, and
# the view turns the choice into group membership.
class UserRoleForm(forms.Form):
    CUSTOMER = 'Customer'
    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (EMPLOYEE, 'Employee'),
        (OWNER, 'Owner'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Role')
