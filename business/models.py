from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from accounts.models import CustomUser, CountryModel
import requests
from pathlib import Path

BUSINESS_CATEGORY_CHOICES = (
    ('bar', 'Bar'),
    ('restaurant', 'Restaurant'),
    ('cafe', 'Café'),
    ('other', 'Other')
)


class BusinessCategory(models.Model):
    category_name = models.CharField(choices=BUSINESS_CATEGORY_CHOICES, default='Other', max_length=20)
    icon = models.ImageField(null=True, blank=True)

    def __str__(self):
        return str(self.category_name)


class BusinessModel(models.Model):
    manager = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    business_name = models.CharField(max_length=100, blank=False, unique=True)
    category = models.ForeignKey(BusinessCategory, on_delete=models.DO_NOTHING, null=True, blank=True)
    short_description = models.TextField()
    email = models.EmailField(blank=False, unique=True)
    phone_nr = models.CharField(max_length=30, blank=False, unique=True)
    country = models.ForeignKey(CountryModel, on_delete=models.SET_NULL, null=True, blank=True)
    maps_address = models.CharField(max_length=100, blank=False)
    displayed_address = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(blank=True, unique=True, max_length=120)
    is_active = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    all_tables = models.IntegerField(blank=True, default=0)
    available_tables = models.IntegerField(blank=True, null=True, default=0)
    is_open_now = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.business_name)
        super(BusinessModel, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.business_name)


class TableModel(models.Model):
    business = models.ForeignKey(BusinessModel, on_delete=models.CASCADE)
    table_nr = models.IntegerField()
    qr_code = models.ImageField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            url = f'https://api.qrserver.com/v1/create-qr-code/?data=tray/generate_order/{self.business.slug}/{self.table_nr}&size=300x300&format=png'
            req = requests.get(url)
            path = f'..\\media\\qr\\{self.business.business_name}'
            Path(path).mkdir(exist_ok=True)

            image = open(f'{path}\\{self.business.slug}_{self.table_nr}.png', 'wb+')
            image.write(req.content)
            image.close()

            self.qr_code = f'{path}\\{self.business.slug}_{self.table_nr}.png'

        super(TableModel, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.table_nr)


class ProductCategory(models.Model):
    business = models.ForeignKey(BusinessModel, on_delete=models.CASCADE, null=True, blank=True)
    category_name = models.CharField(max_length=25)
    slug = models.SlugField(blank=True, null=True)
    icon = models.ImageField(default='beer.png', null=True, blank=True)

    def __str__(self):
        return str(self.category_name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(ProductCategory, self).save(*args, **kwargs)


class ProductModel(models.Model):
    business = models.ForeignKey(BusinessModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=False)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.name)

# class GenericValueModel(models.Model):
#     assoc = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
#     name = models.CharField(max_length=255)
#     value = models.CharField(max_length=255)
