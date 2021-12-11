# Generated by Django 3.0.6 on 2020-06-07 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mintatanterv', '0014_auto_20200604_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mintatantervtargy',
            name='elofeltetel_targy',
            field=models.ManyToManyField(blank=True, related_name='ezenmintatantervtargyakelofeltetele', to='mintatanterv.Targy', verbose_name='előfeltétel tárgy'),
        ),
        migrations.AlterField(
            model_name='targy',
            name='elofeltetel_targy',
            field=models.ManyToManyField(blank=True, related_name='ezentargyakelofeltetele', to='mintatanterv.Targy', verbose_name='előfeltétel tárgy'),
        ),
    ]
