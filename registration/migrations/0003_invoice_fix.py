# Generated by Django 2.0.5 on 2018-09-16 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0002_attendee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoicedetail',
            name='amount',
            field=models.IntegerField(help_text='Částka bez DPH', verbose_name='Částka'),
        ),
    ]
