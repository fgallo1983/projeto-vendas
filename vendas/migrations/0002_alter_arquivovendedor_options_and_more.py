# Generated by Django 5.1.6 on 2025-03-01 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendas', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='arquivovendedor',
            options={'verbose_name': 'Arquivo vendendor', 'verbose_name_plural': 'Arquivo vendendores'},
        ),
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'Vendedor', 'verbose_name_plural': 'Vendedores'},
        ),
    ]
