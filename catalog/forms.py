from django import forms

from .models import Category, Product, Subcategory


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


class CheckoutForm(forms.Form):
    ship_full_name = forms.CharField(max_length=200, label='Full name')
    ship_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), label='Address')
    ship_city = forms.CharField(max_length=100, label='City')
    ship_postcode = forms.CharField(max_length=20, label='Postcode')
    ship_country = forms.CharField(max_length=100, label='Country')
    billing_same = forms.BooleanField(required=False, initial=True, label='Billing address is the same as shipping')


class RatingForm(forms.Form):
    stars = forms.IntegerField(min_value=1, max_value=5)
    comment = forms.CharField(required=False)


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
