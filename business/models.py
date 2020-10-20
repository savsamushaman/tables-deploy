from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from accounts.models import CustomUser


class BusinessModel(models.Model):
    manager = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    business_name = models.CharField(max_length=100, blank=False, unique=True)
    short_description = models.TextField()
    email = models.EmailField(blank=False, unique=True)
    phone_nr = models.CharField(max_length=30, blank=False, unique=True)
    address = models.CharField(max_length=100, blank=False)
    slug = models.SlugField(blank=True)
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
