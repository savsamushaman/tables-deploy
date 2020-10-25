from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=150, blank=True)
    slug = models.SlugField(blank=True)
    email = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        super(CustomUser, self).save(*args, **kwargs)
