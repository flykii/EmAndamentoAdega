# Generated by Django 4.2 on 2023-05-17 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdv', '0009_alter_venda_forma_pagamento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venda',
            name='forma_pagamento',
            field=models.CharField(max_length=20),
        ),
    ]
