# Generated by Django 5.1.6 on 2025-03-06 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendas', '0010_remove_produto_quantidade_alter_venda_valor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venda',
            name='valor',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
