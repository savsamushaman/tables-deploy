# Generated by Django 3.1.2 on 2020-12-02 11:19

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('business', '0045_tablemodel_current_guests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tablemodel',
            name='current_guests',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
