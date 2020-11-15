from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class CountryModel(models.Model):
    name = models.CharField(max_length=50)
    currency = models.CharField(max_length=3, default='-', null=True, blank=True)

    def __str__(self):
        return str(self.name)


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    email = models.EmailField(blank=False, null=True)
    country = models.ForeignKey(CountryModel, on_delete=models.DO_NOTHING, null=True, blank=True)
    device = models.CharField(max_length=16, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        if self.username:
            return str(self.username)
        else:
            return 'Anonymous User'
