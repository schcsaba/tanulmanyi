# Generated by Django 3.0.6 on 2020-06-07 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mintatanterv', '0016_auto_20200607_1855'),
    ]

    operations = [
        migrations.AddField(
            model_name='oktato',
            name='megjelenites',
            field=models.BooleanField(default=False, help_text='Megjelenjen-e az oktató az oktatók előrhetősége oldalon?', verbose_name='Megjelenítés'),
        ),
    ]
