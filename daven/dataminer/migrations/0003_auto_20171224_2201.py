# Generated by Django 2.0 on 2017-12-24 22:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataminer', '0002_auto_20171224_2157'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bourse',
            options={'ordering': ['name'], 'verbose_name': 'bourse', 'verbose_name_plural': 'bources'},
        ),
        migrations.AlterModelOptions(
            name='currency',
            options={'ordering': ['name'], 'verbose_name': 'currency', 'verbose_name_plural': 'currencies'},
        ),
        migrations.AlterModelOptions(
            name='pair',
            options={'ordering': ['name'], 'verbose_name': 'pair', 'verbose_name_plural': 'pairs'},
        ),
    ]
