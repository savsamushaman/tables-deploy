from django import forms
from django.forms import ModelForm

from .models import BusinessModel, ProductModel, ProductCategory, TableModel


class CreateBusinessForm(ModelForm):
    class Meta:
        model = BusinessModel
        fields = '__all__'
        exclude = ['manager', 'slug', 'date_created', 'available_tables', 'all_tables', 'is_active', 'is_open_now',
                   'current_guests']

    business_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input--style-5', 'placeholder': 'How is your place called ?'}))
    short_description = forms.CharField(required=False,
                                        widget=forms.Textarea(
                                            attrs={'rows': 7, 'col': 10, 'class': 'input--style-5',
                                                   'placeholder': 'Describe your place in a few words. (optional)'}))
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'input--style-5', 'placeholder': 'Contact Email Address'}))
    phone_nr = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input--style-5', 'placeholder': 'Contact Phone Number'}))
    maps_address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input--style-5', 'placeholder': 'Café de Flore, Paris'}))
    displayed_address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input--style-5', 'placeholder': '172 Boulevard Saint-Germain'}))
    max_capacity = forms.IntegerField(min_value=0,
                                      widget=forms.NumberInput(
                                          attrs={'class': 'input--style-5', 'placeholder': 'Max Capacity'}))

    def clean(self):
        super(CreateBusinessForm, self).clean()

        max_capacity = self.cleaned_data.get('max_capacity')
        if isinstance(max_capacity, type(None)):
            self._errors['max_capacity'] = self.error_class(['Max capacity cannot be less than 0'])

        return self.cleaned_data


class UpdateBusinessForm(ModelForm):
    class Meta:
        model = BusinessModel
        fields = '__all__'
        exclude = ['manager', 'slug', 'date_created', 'all_tables', 'available_tables', 'is_active', 'current_guests']

    business_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input--style-5', }))
    short_description = forms.CharField(required=False,
                                        widget=forms.Textarea(
                                            attrs={'rows': 7, 'col': 10, 'class': 'input--style-5', }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input--style-5'}))
    phone_nr = forms.CharField(widget=forms.TextInput(attrs={'class': 'input--style-5', }))
    maps_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'input--style-5', }))
    displayed_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'input--style-5', }))
    max_capacity = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'input--style-5'}))

    def clean(self):
        super(UpdateBusinessForm, self).clean()

        max_capacity = self.cleaned_data.get('max_capacity')
        if isinstance(max_capacity, type(None)):
            self._errors['max_capacity'] = self.error_class(['Max capacity cannot be less than 0'])

        return self.cleaned_data


class ProductForm(ModelForm):
    class Meta:
        model = ProductModel
        fields = '__all__'
        exclude = ['business']

    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input--style-5', 'placeholder': 'Product Name'}))
    description = forms.CharField(required=False,
                                  widget=forms.Textarea(
                                      attrs={'class': 'input--style-5', 'placeholder': 'Ingredients or other details'}))
    price = forms.DecimalField(min_value=0, max_digits=10, decimal_places=2,
                               widget=forms.NumberInput(attrs={'class': 'input--style-5', }))

    def clean(self):
        super(ProductForm, self).clean()

        price = self.cleaned_data.get('price')
        if isinstance(price, type(None)):
            self._errors['price'] = self.error_class(['Price cannot be less than 0'])

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        slug = kwargs.pop('slug', None)
        super(ProductForm, self).__init__(*args, **kwargs)

        if slug:
            self.fields['category'].queryset = ProductCategory.objects.filter(business__slug=slug, deleted=False)


class TableForm(ModelForm):
    class Meta:
        model = TableModel
        fields = ['table_nr']

    table_nr = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'input--style-5', 'placeholder': 'Table number'}))


class UpdateTableForm(ModelForm):
    class Meta:
        model = TableModel
        fields = ['table_nr', 'qr_code']

    table_nr = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'input--style-5', 'placeholder': 'Table number'}))


class MenuPointForm(ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['category_name']

    category_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input--style-5', 'placeholder': 'Menu Point name'}))
