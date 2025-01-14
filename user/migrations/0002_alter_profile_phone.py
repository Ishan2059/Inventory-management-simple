# Generated by Django 5.1.3 on 2024-11-22 07:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=models.CharField(blank=True, max_length=10, null=True, validators=[django.core.validators.RegexValidator(message='Phone number must be 10 digits.', regex='^\\d{10}$')]),
        ),
    ]
