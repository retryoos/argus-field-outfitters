from django import forms
from django.core.validators import RegexValidator

from .models import Category, Product, Subcategory

# A plain list rather than a third party package, kept short on purpose, this
# is every country a shopper might realistically ship to, sorted so the
# dropdown is easy to scan.
COUNTRY_CHOICES = [(name, name) for name in [
    'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Argentina',
    'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain',
    'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin',
    'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil',
    'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon',
    'Canada', 'Chad', 'Chile', 'China', 'Colombia', 'Costa Rica', 'Croatia',
    'Cuba', 'Cyprus', 'Czechia', 'Denmark', 'Djibouti', 'Dominican Republic',
    'Ecuador', 'Egypt', 'El Salvador', 'Estonia', 'Ethiopia', 'Fiji',
    'Finland', 'France', 'Gabon', 'Georgia', 'Germany', 'Ghana', 'Greece',
    'Greenland', 'Guatemala', 'Guinea', 'Haiti', 'Honduras', 'Hungary',
    'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel',
    'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kuwait',
    'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Liberia', 'Libya',
    'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi',
    'Malaysia', 'Maldives', 'Mali', 'Malta', 'Mexico', 'Moldova', 'Monaco',
    'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia',
    'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria',
    'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Panama',
    'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland',
    'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saudi Arabia',
    'Senegal', 'Serbia', 'Singapore', 'Slovakia', 'Slovenia', 'Somalia',
    'South Africa', 'South Korea', 'Spain', 'Sri Lanka', 'Sudan', 'Sweden',
    'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand',
    'Tunisia', 'Turkey', 'Turkmenistan', 'Uganda', 'Ukraine',
    'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay',
    'Uzbekistan', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe',
]]

postcode_validator = RegexValidator(
    regex=r'^\d{1,5}$',
    message='Enter a postcode of up to 5 digits.',
)


class ProductFilterForm(forms.Form):
    min_price = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min'}),
    )
    max_price = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max'}),
    )
    brand = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    color = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    size = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    subcategory = forms.ModelChoiceField(
        required=False, queryset=Subcategory.objects.all(), empty_label='Any',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    in_stock = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def __init__(self, *args, **kwargs):
        # The choices are rebuilt every time the form is created, so a brand
        # or color added through the backoffice shows up in the filter
        # without a code change.
        super().__init__(*args, **kwargs)
        self.fields['brand'].choices = self.value_choices('brand')
        self.fields['color'].choices = self.value_choices('color')
        self.fields['size'].choices = self.value_choices('size_variant')

    def value_choices(self, field_name):
        # The dropdown options are read from the products themselves so the
        # filter only ever offers values that exist in the catalogue.
        values = (Product.objects
                  .exclude(**{field_name: ''})
                  .values_list(field_name, flat=True)
                  .distinct()
                  .order_by(field_name))
        return [('', 'Any')] + [(value, value) for value in values]


# save_address is opt in and checked by default, ticking it off copies the
# shipping fields onto the shopper's Profile so next checkout can prefill them.
class CheckoutForm(forms.Form):
    ship_full_name = forms.CharField(max_length=200, label='Full name')
    ship_address = forms.CharField(max_length=255, widget=forms.Textarea(attrs={'rows': 2}), label='Address')
    ship_city = forms.CharField(max_length=100, label='City')
    ship_postcode = forms.CharField(max_length=5, label='Postcode', validators=[postcode_validator])
    ship_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label='Country')
    save_address = forms.BooleanField(required=False, initial=True, label='Save this address for next time')


# This is where the 1 to 5 star range is actually enforced, the model field
# itself has no bounds.
class RatingForm(forms.Form):
    stars = forms.IntegerField(min_value=1, max_value=5)
    comment = forms.CharField(required=False)


# min_value=0 is intentional, setting the quantity to 0 in the cart is how a
# line gets removed, the view treats that as a delete rather than an error.
class CartUpdateForm(forms.Form):
    quantity = forms.IntegerField(min_value=0, max_value=99)


# These three ModelForms live in catalog rather than backoffice because
# backoffice imports them directly for its product, category, and
# subcategory CRUD screens.
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'brand', 'subcategory', 'price', 'size_variant', 'color', 'description', 'image', 'stock']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['category', 'name', 'slug']
