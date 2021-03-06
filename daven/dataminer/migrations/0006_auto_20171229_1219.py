# Generated by Django 2.0 on 2017-12-29 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataminer', '0005_auto_20171226_1749'),
    ]

    operations = [
        migrations.AddField(
            model_name='pair',
            name='fee',
            field=models.DecimalField(decimal_places=4, default=0.0, max_digits=5),
        ),
        migrations.AddField(
            model_name='pair',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pair',
            name='max_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='pair',
            name='max_price',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='pair',
            name='min_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='pair',
            name='min_price',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='pair',
            name='min_total',
            field=models.FloatField(default=0.0),
        ),
    ]
