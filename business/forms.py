from django.forms import ModelForm
from .models import BusinessModel


class CreateBusinessForm(ModelForm):
    class Meta:
        model = BusinessModel
        fields = '__all__'
        exclude = ['manager', 'slug', 'date_created', 'available_tables', 'is_active', 'is_open_now']
