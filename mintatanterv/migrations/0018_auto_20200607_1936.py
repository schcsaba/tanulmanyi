# Generated by Django 3.0.6 on 2020-06-07 17:36

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('mintatanterv', '0017_oktato_megjelenites'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oktato',
            name='tel',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, verbose_name='telefon'),
        ),
    ]
