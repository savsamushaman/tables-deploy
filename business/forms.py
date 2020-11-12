from django.forms import ModelForm

from .models import BusinessModel, ProductModel, ProductCategory


class CreateBusinessForm(ModelForm):
    class Meta:
        model = BusinessModel
        fields = '__all__'
        exclude = ['manager', 'slug', 'date_created', 'available_tables', 'is_active', 'is_open_now']


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
