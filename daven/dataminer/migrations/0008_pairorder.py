# Generated by Django 2.0 on 2017-12-31 07:36

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dataminer', '0007_auto_20171230_1940'),
    ]

    operations = [
        migrations.CreateModel(
            name='PairOrder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('price', models.FloatField(default=0.0)),
                ('vol', models.FloatField(default=0.0)),
                ('ask', models.BooleanField(default=False)),
                ('bid', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('pair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='dataminer.Pair')),
            ],
            options={
                'verbose_name': 'pair order',
                'verbose_name_plural': 'pair orders',
                'ordering': ['created_at'],
            },
        ),
    ]
