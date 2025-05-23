# Generated by Django 5.2 on 2025-04-22 10:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=220)),
                ('client_id', models.CharField(max_length=14)),
                ('client_address', models.CharField(max_length=220)),
                ('contract_date', models.DateField()),
                ('recieve_date', models.DateField()),
                ('contract_total', models.DecimalField(decimal_places=2, max_digits=9)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_title', models.CharField(max_length=600)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('notes', models.TextField(default=' ')),
                ('Contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='app.contract')),
            ],
        ),
    ]
