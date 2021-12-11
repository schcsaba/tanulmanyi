# Generated by Django 3.0.6 on 2020-06-01 12:22

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('szakdolgozat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemaStatusz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nev', models.CharField(max_length=50, unique='True', verbose_name='név')),
            ],
            options={
                'verbose_name': 'cím státusza',
                'verbose_name_plural': 'címek státuszai',
                'ordering': ['nev'],
            },
        ),
        migrations.CreateModel(
            name='Temavezeto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('elotag', models.CharField(blank=True, max_length=20, verbose_name='előtag')),
                ('vezeteknev', models.CharField(max_length=100, verbose_name='vezetéknév')),
                ('keresztnev', models.CharField(max_length=100, verbose_name='keresztnév')),
                ('neptun_kod', models.CharField(max_length=6, verbose_name='neptun kód')),
                ('max_letszam', models.IntegerField(verbose_name='maximális létszám')),
                ('tel', phonenumber_field.modelfields.PhoneNumberField(blank=True, default='+00000000000', max_length=128, region=None, verbose_name='telefon')),
                ('email', models.EmailField(max_length=254, verbose_name='email')),
                ('avatott_nev', models.CharField(blank=True, max_length=100, verbose_name='avatott név')),
                ('valaszthato', models.BooleanField(default=False, verbose_name='választható')),
            ],
            options={
                'verbose_name': 'témavezető',
                'verbose_name_plural': 'témavezetők',
                'ordering': ['vezeteknev', 'keresztnev'],
            },
        ),
        migrations.CreateModel(
            name='TemavezetoTemakor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rejtett', models.BooleanField(default=False, verbose_name='rejtett')),
                ('temakor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='szakdolgozat.Temakor', verbose_name='téma')),
                ('temavezeto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='szakdolgozat.Temavezeto', verbose_name='témavezető')),
            ],
            options={
                'verbose_name': 'témavezető témája',
                'verbose_name_plural': 'témavezetők témái',
                'ordering': ['temavezeto', 'temakor'],
                'unique_together': {('temavezeto', 'temakor')},
            },
        ),
        migrations.AddField(
            model_name='temavezeto',
            name='temakorok',
            field=models.ManyToManyField(blank=True, through='szakdolgozat.TemavezetoTemakor', to='szakdolgozat.Temakor', verbose_name='témák'),
        ),
        migrations.CreateModel(
            name='Tema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cim', models.CharField(max_length=255, unique='True', verbose_name='cím')),
                ('idegen_nyelv_szukseges', models.CharField(blank=True, max_length=500, verbose_name='idegen nyelv szükséges')),
                ('megjegyzes', models.CharField(blank=True, max_length=500, verbose_name='megjegyzés')),
                ('tema_statusz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='szakdolgozat.TemaStatusz', verbose_name='cím státusza')),
                ('temavezeto_temakor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='szakdolgozat.TemavezetoTemakor', verbose_name='témavezető témája')),
            ],
            options={
                'verbose_name': 'cím',
                'verbose_name_plural': 'címek',
                'ordering': ['temavezeto_temakor', 'cim'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='temavezeto',
            unique_together={('vezeteknev', 'keresztnev', 'neptun_kod')},
        ),
    ]
