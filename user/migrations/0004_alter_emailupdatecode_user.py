# Generated by Django 5.0.7 on 2024-08-03 06:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_emailupdatecode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailupdatecode',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]