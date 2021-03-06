# Generated by Django 3.0.6 on 2020-06-04 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mintatanterv', '0007_kepzesiszint'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kepzes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nev', models.CharField(max_length=200, verbose_name='név')),
                ('kepzesi_szint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mintatanterv.KepzesiSzint', verbose_name='képzési szint')),
            ],
            options={
                'verbose_name': 'képzés',
                'verbose_name_plural': 'képzések',
            },
        ),
    ]
