# Generated by Django 4.2 on 2023-05-17 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdv', '0006_venda_forma_pagamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='venda',
            name='total_venda',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=8),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='venda',
            name='data',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]