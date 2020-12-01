from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.text import slugify


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class CountryModel(models.Model):
    name = models.CharField(max_length=50)
    currency = models.CharField(max_length=3, default='-', null=True, blank=True)

    def __str__(self):
        return str(self.name)


class CustomUser(AbstractUser):
    objects = CustomUserManager()

    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    slug = models.SlugField(blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=True)
    country = models.ForeignKey(CountryModel, on_delete=models.SET_NULL, null=True, blank=True)
    device = models.CharField(max_length=16, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        if not self.username:
            self.username = 'Anonymous-' + str(self.pk)
        super(CustomUser, self).save(*args, **kwargs)
