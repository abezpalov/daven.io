# Generated by Django 2.0.1 on 2018-01-31 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataminer', '0016_auto_20180131_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='pairjsoninfo',
            name='content',
            field=models.TextField(null=True),
        ),
    ]
