# Generated by Django 2.0.5 on 2018-11-04 07:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0004_attendee_attended'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=256, verbose_name='Lector name')),
            ],
            options={
                'verbose_name': 'Školitel',
                'verbose_name_plural': 'Školitelé',
            },
        ),
        migrations.RemoveField(
            model_name='courseevent',
            name='location',
        ),
        migrations.AddField(
            model_name='courseevent',
            name='address',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='registration.Address', verbose_name='Místo konání'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coursetype',
            name='certificate_content',
            field=models.TextField(default=None, verbose_name='Obsah certifikátu'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coursetype',
            name='certificate_template',
            field=models.TextField(choices=[('qgis-zacatecnik.tex', 'qgis-zacatecnik.tex'), ('postgis-zacatecnik.tex', 'postgis-zacatecnik.tex'), ('geopython-zacatecnik.tex', 'geopython-zacatecnik.tex'), ('postgis-pokrocily.tex', 'postgis-pokrocily.tex'), ('qgis-pokrocily.tex', 'qgis-pokrocily.tex'), ('grass-gis-zacatecnik.tex', 'grass-gis-zacatecnik.tex')], default=None, verbose_name='Šablona certifikátu'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='courseattendee',
            name='attended',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coursetype',
            name='lectors',
            field=models.ManyToManyField(to='registration.Lector'),
        ),
    ]