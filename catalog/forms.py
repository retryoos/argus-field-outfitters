from django import forms

from .models import Product, Subcategory


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
        super().__init__(*args, **kwargs)
        self.fields['brand'].choices = self.value_choices('brand')
        self.fields['color'].choices = self.value_choices('color')
        self.fields['size'].choices = self.value_choices('size_variant')

    def value_choices(self, field_name):
        values = (Product.objects
                  .exclude(**{field_name: ''})
                  .values_list(field_name, flat=True)
                  .distinct()
                  .order_by(field_name))
        return [('', 'Any')] + [(value, value) for value in values]
