# Generated by Django 3.0.7 on 2020-06-09 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('szabalyzat', '0002_szabalyzat_szabalyzatfajl'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='szabalyzat',
            name='link',
        ),
        migrations.AlterField(
            model_name='szabalyzat',
            name='szabalyzatfajl',
            field=models.FileField(upload_to='szabalyzatok/', verbose_name='szabályzatfájl'),
        ),
    ]
