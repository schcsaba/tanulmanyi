# Generated by Django 3.0.6 on 2020-06-04 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mintatanterv', '0006_oktato'),
    ]

    operations = [
        migrations.CreateModel(
            name='KepzesiSzint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nev', models.CharField(max_length=100, unique='True', verbose_name='név')),
            ],
            options={
                'verbose_name': 'képzési szint',
                'verbose_name_plural': 'képzési szintek',
            },
        ),
    ]
