# Generated by Django 5.1.6 on 2025-03-08 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendas', '0011_alter_venda_valor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='valor',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='venda',
            name='valor',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
    ]
