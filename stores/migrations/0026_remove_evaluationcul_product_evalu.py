# Generated by Django 3.2.5 on 2023-01-17 13:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0025_evaluationcul_product_evalu'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evaluationcul',
            name='product_evalu',
        ),
    ]
