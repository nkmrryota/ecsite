# Generated by Django 3.2.5 on 2022-11-27 08:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0008_productevaluations_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productevaluations',
            name='product',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='related_evaluation', to='stores.products'),
        ),
    ]
