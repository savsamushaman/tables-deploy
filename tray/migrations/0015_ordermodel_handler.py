# Generated by Django 3.1.2 on 2021-01-03 12:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tray', '0014_ordermodel_new'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermodel',
            name='handler',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='handler', to=settings.AUTH_USER_MODEL),
        ),
    ]
