from decimal import Decimal
from pathlib import Path

import requests
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import CustomUser, CountryModel

BUSINESS_CATEGORY_CHOICES = (
    ('Bar', 'Bar'),
    ('Restaurant', 'Restaurant'),
    ('Café', 'Cafe'),
    ('Club', 'Club'),
    ('Other', 'Other')

)

INVITATION_CHOICES = (
    ('S', 'Sent'),
    ('A', 'Accepted'),
    ('D', 'Declined'),
    ('C', 'Canceled')
)


class BusinessCategory(models.Model):
    category_name = models.CharField(choices=BUSINESS_CATEGORY_CHOICES, default='Other', max_length=20)
    icon = models.ImageField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Business Category models'

    def __str__(self):
        return str(self.category_name)


class BusinessModel(models.Model):
    manager = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    business_name = models.CharField(max_length=200, blank=False, unique=True)
    category = models.ForeignKey(BusinessCategory, on_delete=models.DO_NOTHING, null=True)
    short_description = models.TextField()
    email = models.EmailField(unique=True)
    phone_nr = models.CharField(max_length=30, unique=True)
    country = models.ForeignKey(CountryModel, on_delete=models.DO_NOTHING)
    maps_address = models.CharField(max_length=100)
    displayed_address = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, unique=True, max_length=120)
    date_created = models.DateTimeField(default=timezone.now)
    max_capacity = models.IntegerField(default=0)
    current_guests = models.IntegerField(default=0)
    all_tables = models.IntegerField(default=0)
    available_tables = models.IntegerField(blank=True, null=True, default=0)
    is_open_now = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    staff = models.ManyToManyField(CustomUser, blank=True, related_name='staff', )
    admins = models.ManyToManyField(CustomUser, blank=True, related_name='admins', )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.business_name)
        super(BusinessModel, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.business_name)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(all_tables__gte=Decimal('0')), name='all_tables_gt_0'),
            models.CheckConstraint(check=models.Q(available_tables__gte=Decimal('0')), name='available_tables_gt_0'),
            models.CheckConstraint(check=models.Q(max_capacity__gte=Decimal('0')), name='max_capacity_gt_0'),
            models.CheckConstraint(check=models.Q(current_guests__gte=Decimal('0')), name='current_guests_gt_0'),
        ]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ must change URL ON RELEASE

class TableModel(models.Model):
    business = models.ForeignKey(BusinessModel, on_delete=models.CASCADE)
    table_nr = models.IntegerField()
    qr_code = models.ImageField(blank=True, null=True)
    locked = models.BooleanField(default=False)
    current_guests = models.ManyToManyField(CustomUser, blank=True)

    def __init__(self, *args, **kwargs):
        super(TableModel, self).__init__(*args, **kwargs)
        self.old_table_nr = self.table_nr

    def save(self, *args, **kwargs):
        if not self.qr_code or self.old_table_nr != self.table_nr:
            url = f'https://api.qrserver.com/v1/create-qr-code/?data=http://127.0.0.1:8000/tray/generate_order/{self.business.slug}/{self.table_nr}&size=300x300&format=png'
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

    def str_table_nr(self):
        return str(self.table_nr)

    class Meta:
        unique_together = ('business', 'table_nr')


class ProductCategory(models.Model):
    business = models.ForeignKey(BusinessModel, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=25)
    slug = models.SlugField(blank=True, null=True)
    icon = models.ImageField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.category_name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(ProductCategory, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('business', 'category_name')
        verbose_name_plural = 'Product Category models'


class ProductModel(models.Model):
    business = models.ForeignKey(BusinessModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, blank=True, null=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=Decimal('0')), name='price_gt_0'),
        ]

    def __str__(self):
        return str(self.name)


class Invitation(models.Model):
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='to_user')
    business = models.ForeignKey(BusinessModel, on_delete=models.CASCADE)
    status = models.CharField(choices=INVITATION_CHOICES, default='Sent', max_length=15)

    def __str__(self):
        return f'from : {str(self.from_user)} - to : {str(self.to_user)} / {self.business.business_name}'

# class GenericValueModel(models.Model):
#     assoc = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
#     name = models.CharField(max_length=255)
#     value = models.CharField(max_length=255)
