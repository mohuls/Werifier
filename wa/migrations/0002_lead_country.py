# Generated by Django 4.0.3 on 2022-03-07 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wa', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='country',
            field=models.CharField(default='Bangladesh', max_length=100),
            preserve_default=False,
        ),
    ]
