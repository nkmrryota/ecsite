# Generated by Django 3.2.5 on 2023-01-04 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0021_auto_20230101_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='address',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitems',
            name='chekeout_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='prefecture',
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitems',
            name='zip_code',
            field=models.CharField(default=1, max_length=8),
            preserve_default=False,
        ),
    ]
