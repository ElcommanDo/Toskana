# Generated by Django 5.2 on 2025-04-22 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_contract_remain_alter_contract_contract_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='remain',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
