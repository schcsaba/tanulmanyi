# Generated by Django 3.0.6 on 2020-06-04 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mintatanterv', '0008_kepzes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Szak',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nev', models.CharField(max_length=200, verbose_name='név')),
                ('kepzes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mintatanterv.Kepzes', verbose_name='képzés')),
            ],
            options={
                'verbose_name': 'szak',
                'verbose_name_plural': 'szakok',
                'unique_together': {('nev', 'kepzes')},
            },
        ),
    ]
