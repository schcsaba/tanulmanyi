# Generated by Django 3.0.7 on 2020-06-09 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('szabalyzat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='szabalyzat',
            name='szabalyzatfajl',
            field=models.FileField(blank=True, upload_to='szabalyzatok/', verbose_name='szabályzatfájl'),
        ),
    ]
