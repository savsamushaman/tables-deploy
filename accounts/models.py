from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class CountryModel(models.Model):
    name = models.CharField(max_length=50)
    currency = models.CharField(max_length=3, default='-', null=True, blank=True)

    def __str__(self):
        return str(self.name)


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=150, blank=True)
    slug = models.SlugField(blank=True)
    email = models.EmailField(unique=True)
    country = models.ForeignKey(CountryModel, on_delete=models.DO_NOTHING, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        super(CustomUser, self).save(*args, **kwargs)
