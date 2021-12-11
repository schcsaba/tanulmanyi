# Generated by Django 3.0.6 on 2020-06-04 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mintatanterv', '0005_oktatotipus'),
    ]

    operations = [
        migrations.CreateModel(
            name='Oktato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('elotag', models.CharField(blank=True, max_length=20, verbose_name='előtag')),
                ('vezeteknev', models.CharField(max_length=100, verbose_name='vezetéknév')),
                ('keresztnev', models.CharField(max_length=100, verbose_name='keresztnév')),
                ('neptun_kod', models.CharField(max_length=6, verbose_name='neptun kód')),
                ('avatott_nev', models.CharField(blank=True, max_length=100, verbose_name='avatott név')),
            ],
            options={
                'verbose_name': 'oktató',
                'verbose_name_plural': 'oktatók',
                'ordering': ['vezeteknev', 'keresztnev'],
                'unique_together': {('vezeteknev', 'keresztnev', 'neptun_kod')},
            },
        ),
    ]
