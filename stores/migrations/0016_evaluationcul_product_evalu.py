# Generated by Django 3.2.5 on 2022-12-04 05:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0015_auto_20221203_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluationcul',
            name='product_evalu',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='related_evalu_col', to='stores.productevaluations'),
            preserve_default=False,
        ),
    ]
