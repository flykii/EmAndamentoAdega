# Generated by Django 4.2 on 2023-05-24 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdv', '0012_venda_vendedor'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='embalagem',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='produto',
            name='unidade_medida',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='venda',
            name='forma_pagamento',
            field=models.CharField(blank=True, choices=[('credito', 'Cartão de Crédito'), ('debito', 'Cartão de Débito'), ('pix', 'PIX'), ('dinheiro', 'Dinheiro'), ('cliente', 'Cliente')], max_length=20, null=True),
        ),
    ]
