# Generated by Django 3.1.1 on 2020-09-27 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('szakdolgozat', '0011_beallitas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beallitas',
            name='ertek',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='érték'),
        ),
    ]
