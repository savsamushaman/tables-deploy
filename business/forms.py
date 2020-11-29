from django import forms
from django.forms import ModelForm

from .models import BusinessModel, ProductModel, ProductCategory


class CreateBusinessForm(ModelForm):
    class Meta:
        model = BusinessModel
        fields = '__all__'
        exclude = ['manager', 'slug', 'date_created', 'available_tables', 'is_active', 'is_open_now']


class UpdateBusinessForm(ModelForm):
    class Meta:
        model = BusinessModel
        fields = '__all__'
        exclude = ['manager', 'slug', 'date_created', 'available_tables', 'is_active']

    business_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input--style-5', }))
    short_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 7, 'col': 10, 'class': 'input--style-5', }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input--style-5'}))
    phone_nr = forms.CharField(widget=forms.TextInput(attrs={'class': 'input--style-5', }))
    maps_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'input--style-5', }))
    displayed_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'input--style-5', }))
    all_tables = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'input--style-5'}))


class CreateProductForm(ModelForm):
    class Meta:
        model = ProductModel
        fields = '__all__'
        exclude = ['business']

    def __init__(self, *args, **kwargs):
        slug = kwargs.pop('slug', None)
        super(CreateProductForm, self).__init__(*args, **kwargs)

        if slug:
            self.fields['category'].queryset = ProductCategory.objects.filter(business__slug=slug)
