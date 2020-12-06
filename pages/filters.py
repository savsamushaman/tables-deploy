import django_filters
from distutils.util import strtobool
from django import forms
from business.models import BusinessCategory, CountryModel, BusinessModel

BOOL_CHOICES = (('None', 'Open or Closed'), ('True', 'Open'), ('False', 'Closed'),)


class BusinessFilter(django_filters.FilterSet):
    class Meta:
        model = BusinessModel
        fields = ['category', 'country', 'displayed_address', 'max_capacity', 'current_guests', 'available_tables',
                  'is_open_now']

    category = django_filters.ModelChoiceFilter(queryset=BusinessCategory.objects.all(),
                                                empty_label='Select Category',
                                                widget=forms.Select(
                                                    attrs={'class': 'filter-field form-control custom-select mr-sm-2',
                                                           'id': 'inputCategory'}))
    country = django_filters.ModelChoiceFilter(queryset=CountryModel.objects.all(),
                                               empty_label='Select Country',
                                               widget=forms.Select(
                                                   attrs={'class': 'form-control custom-select mr-sm-2 filter-field',
                                                          'id': 'inputCountry'}))

    displayed_address = django_filters.CharFilter(lookup_expr='icontains',
                                                  widget=forms.TextInput(
                                                      attrs={'class': 'form-control filter-field', 'type': 'text',
                                                             'id': 'inputAddress', 'placeholder': 'By address',
                                                             'autocomplete': 'off'}))

    max_capacity = django_filters.NumberFilter(min_value=0, lookup_expr='lte', widget=forms.NumberInput(
        attrs={'class': 'form-control filter-field', 'id': 'inputMaxCap', 'placeholder': 'X or less'}))

    current_guests = django_filters.NumberFilter(min_value=0, lookup_expr='lte', widget=forms.NumberInput(
        attrs={'class': 'form-control filter-field', 'id': 'inputCurrGuests', 'placeholder': 'X or less'}))
    available_tables = django_filters.NumberFilter(min_value=0, lookup_expr='lte', widget=forms.NumberInput(
        attrs={'class': 'form-control filter-field', 'id': 'inputAvailTables', 'placeholder': 'X or less'}))

    is_open_now = django_filters.TypedChoiceFilter(choices=BOOL_CHOICES, coerce=strtobool,
                                                   widget=forms.Select(attrs={
                                                       'class': 'form-control custom-select mr-sm-2 filter-field'
                                                   }))
