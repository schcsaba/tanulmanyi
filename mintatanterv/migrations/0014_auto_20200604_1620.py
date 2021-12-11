# Generated by Django 3.0.6 on 2020-06-04 14:20

from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('mintatanterv', '0013_auto_20200604_1526'),
    ]

    operations = [
        migrations.CreateModel(
            name='Felev',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('felev', models.CharField(max_length=9, unique=True, verbose_name='félév')),
                ('aktualis', models.BooleanField(default=False, verbose_name='aktuális')),
            ],
            options={
                'verbose_name': 'félév',
                'verbose_name_plural': 'félévek',
            },
        ),
        migrations.CreateModel(
            name='FelvetelTipusa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nev', models.CharField(max_length=50, unique='True', verbose_name='név')),
            ],
            options={
                'verbose_name': 'felvétel típusa',
                'verbose_name_plural': 'felvétel típusai',
            },
        ),
        migrations.CreateModel(
            name='Mintatanterv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kod', models.CharField(max_length=10, unique='True', verbose_name='kód')),
                ('nev', models.CharField(max_length=200, verbose_name='név')),
                ('aktualis', models.BooleanField(default=False, help_text='Az itt kijelölt mintatantervek tárgyainak kurzusai jelennek meg az oktatók őszi és tavaszi kurzuslistáiban.', verbose_name='aktuális')),
                ('specializacio', models.ManyToManyField(blank=True, related_name='mintatantervspecializacio', to='mintatanterv.Specializacio', verbose_name='specializáció')),
                ('szak', models.ManyToManyField(blank=True, related_name='mintatantervszak', to='mintatanterv.Szak', verbose_name='szak')),
                ('szakirany', models.ManyToManyField(blank=True, related_name='mintatantervszakirany', to='mintatanterv.Szakirany', verbose_name='szakirány')),
            ],
            options={
                'verbose_name': 'mintatanterv',
                'verbose_name_plural': 'mintatantervek',
                'ordering': ['kod'],
            },
        ),
        migrations.CreateModel(
            name='MintatantervTargy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('felev', models.IntegerField(verbose_name='félév')),
                ('kredit', models.IntegerField(blank=True, null=True, verbose_name='kredit')),
                ('oszi_tavaszi', models.BooleanField(default=False, verbose_name='őszi és tavaszi félévben is indul')),
            ],
            options={
                'verbose_name': 'mintatanterv tárgy',
                'verbose_name_plural': 'mintatantervek tárgyai',
            },
        ),
        migrations.CreateModel(
            name='Nyelv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nev', models.CharField(max_length=50, unique=True, verbose_name='név')),
            ],
            options={
                'verbose_name': 'nyelv',
                'verbose_name_plural': 'nyelvek',
            },
        ),
        migrations.CreateModel(
            name='Targy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('targykod', models.CharField(max_length=20, unique='True', verbose_name='tárgykód')),
                ('targynev', models.CharField(max_length=200, verbose_name='tárgynév')),
                ('kredit', models.IntegerField(verbose_name='kredit')),
                ('cel', tinymce.models.HTMLField(blank=True, max_length=100000, null=True, verbose_name='A tantárgy elsajátításának célja')),
                ('targyleiras', tinymce.models.HTMLField(blank=True, max_length=100000, null=True, verbose_name='Tantárgyi program')),
                ('modszertan', tinymce.models.HTMLField(blank=True, max_length=100000, null=True, verbose_name='Módszertan')),
                ('evkozi_kov', tinymce.models.HTMLField(blank=True, max_length=100000, null=True, verbose_name='Évközi tanulmányi követelmények')),
                ('vegso_kov', tinymce.models.HTMLField(blank=True, max_length=100000, null=True, verbose_name='A félévvégi érdemjegy megszerzésének követelményei')),
                ('kotelezo_olvasmanyok', tinymce.models.HTMLField(blank=True, max_length=100000, null=True, verbose_name='Kötelező olvasmányok')),
                ('ajanlott_irodalom', tinymce.models.HTMLField(blank=True, max_length=100000, null=True, verbose_name='Ajánlott irodalom')),
                ('ekvivalens_targy', models.ManyToManyField(blank=True, related_name='_targy_ekvivalens_targy_+', to='mintatanterv.Targy', verbose_name='ekvivalens tárgy')),
                ('elofeltetel_targy', models.ManyToManyField(blank=True, to='mintatanterv.Targy', verbose_name='előfeltétel tárgy')),
                ('kovetelmeny', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mintatanterv.Kovetelmeny', verbose_name='követelmény')),
                ('kurzustipus', models.ManyToManyField(blank=True, to='mintatanterv.Kurzustipus', verbose_name='kurzustípus')),
                ('mintatanterv', models.ManyToManyField(blank=True, related_name='targymintatantervei', through='mintatanterv.MintatantervTargy', to='mintatanterv.Mintatanterv', verbose_name='tárgy mintatantervei')),
            ],
            options={
                'verbose_name': 'tárgy',
                'verbose_name_plural': 'tárgyak',
                'ordering': ['targykod'],
            },
        ),
        migrations.CreateModel(
            name='TargyOktato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oktato', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mintatanterv.Oktato', verbose_name='tárgyoktató')),
                ('oktato_tipus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mintatanterv.Oktatotipus', verbose_name='oktató típus')),
                ('targy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mintatanterv.Targy', verbose_name='tárgy')),
            ],
            options={
                'verbose_name': 'tárgy oktató',
                'verbose_name_plural': 'tárgyak oktatói',
                'unique_together': {('targy', 'oktato', 'oktato_tipus')},
            },
        ),
        migrations.CreateModel(
            name='TargyMunkarend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kurzuskod', models.CharField(max_length=20, unique=True, verbose_name='kurzuskód')),
                ('orarend_oraszam', models.IntegerField(verbose_name='órarend óraszám')),
                ('max_hianyzas', models.IntegerField(verbose_name='max hiányzás')),
                ('akkr_oraszam', models.IntegerField(verbose_name='akkreditált óraszám')),
                ('max_letszam', models.IntegerField(blank=True, null=True, verbose_name='maximális létszám')),
                ('lejelentkezes_letiltva', models.BooleanField(default=False, verbose_name='Lejelentkezés letiltva')),
                ('jelentkezes_letiltva', models.BooleanField(default=False, verbose_name='Jelentkezés letiltva')),
                ('megjegyzes', models.CharField(blank=True, max_length=300, null=True, verbose_name='megjegyzés')),
                ('kurzusfelveteli_kovetelmeny', models.CharField(blank=True, max_length=500, null=True, verbose_name='kurzusfelvételi követelmény')),
                ('kurzusfelveteli_kovetelmeny_leiras', models.CharField(blank=True, max_length=500, null=True, verbose_name='kurzusfelvételi követelmény leírás')),
                ('nem_indul', models.BooleanField(default=False, verbose_name='nem indul')),
                ('belso_megjegyzes', models.CharField(blank=True, max_length=300, null=True, verbose_name='belső megjegyzés')),
                ('kurzustipus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mintatanterv.Kurzustipus', verbose_name='kurzustípus')),
                ('munkarend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mintatanterv.Munkarend', verbose_name='munkarend')),
                ('nyelv', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='mintatanterv.Nyelv', verbose_name='nyelv')),
                ('oktato', models.ManyToManyField(blank=True, related_name='targymunkarendoktato', to='mintatanterv.Oktato', verbose_name='kurzusoktató')),
                ('targy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mintatanterv.Targy', verbose_name='tárgy')),
                ('vizsgatipus', models.ManyToManyField(blank=True, to='mintatanterv.Vizsgatipus', verbose_name='vizsgatípus')),
            ],
            options={
                'verbose_name': 'tárgy kurzus',
                'verbose_name_plural': 'tárgyak kurzusai',
            },
        ),
        migrations.AddField(
            model_name='targy',
            name='munkarend',
            field=models.ManyToManyField(blank=True, through='mintatanterv.TargyMunkarend', to='mintatanterv.Munkarend', verbose_name='kurzus'),
        ),
        migrations.AddField(
            model_name='targy',
            name='nagytargy',
            field=models.ManyToManyField(blank=True, related_name='nagytargy', to='mintatanterv.NagyTargy', verbose_name='nagytárgy'),
        ),
        migrations.AddField(
            model_name='targy',
            name='oktato',
            field=models.ManyToManyField(blank=True, through='mintatanterv.TargyOktato', to='mintatanterv.Oktato', verbose_name='tárgyoktató'),
        ),
        migrations.AddField(
            model_name='mintatantervtargy',
            name='elofeltetel_targy',
            field=models.ManyToManyField(blank=True, related_name='mintatantervtargyelofelteteltargy', to='mintatanterv.Targy', verbose_name='előfeltétel tárgy'),
        ),
        migrations.AddField(
            model_name='mintatantervtargy',
            name='felvetel_tipusa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mintatanterv.FelvetelTipusa', verbose_name='felvétel típusa'),
        ),
        migrations.AddField(
            model_name='mintatantervtargy',
            name='mintatanterv',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mintatanterv.Mintatanterv', verbose_name='mintatanterv'),
        ),
        migrations.AddField(
            model_name='mintatantervtargy',
            name='targy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mintatanterv.Targy', verbose_name='tárgy'),
        ),
        migrations.AddField(
            model_name='mintatanterv',
            name='targy',
            field=models.ManyToManyField(blank=True, related_name='mintatantervtargyai', through='mintatanterv.MintatantervTargy', to='mintatanterv.Targy', verbose_name='tárgy'),
        ),
        migrations.AlterUniqueTogether(
            name='mintatantervtargy',
            unique_together={('mintatanterv', 'targy')},
        ),
    ]
