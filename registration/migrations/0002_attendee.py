# Generated by Django 2.0.5 on 2018-09-16 09:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='token',
            field=models.CharField(default=uuid.UUID('1c771aa3-55da-4a7f-bef3-1b1dea0885e7'), max_length=255, verbose_name='Token'),
        ),
        migrations.AlterField(
            model_name='attendee',
            name='gdpr',
            field=models.BooleanField(help_text='<p>\n            Souhlasím se zpracováním poskytnutých osobních údajů a\n            zařazením do databáze uživatelů společnosti <a\n                    href="http://opengeolabs.cz" target="_blank">OpenGeoLabs s.r.o.</a> se\n            sídlem Brandlova 1559/7, Praha 11, 149 00 (dále jen OpenGeoLabs\n            s.r.o.) pro vlastní použití v souladu s příslušnými ustanoveními zákona\n            č. 101/2000 Sb., o ochraně osobních údajů a o změně některých údajů v\n            platném znění. Beru na vědomí, že údaje budou využívány pouze v rámci\n            společnosti OpenGeoLabs s.r.o.</p>\n            <p>Jsem si vědom/a toho, že souhlas s\n            jejich zpracováním mohu kdykoliv odvolat zasláním e-mailu na adresu\n            <abbr title="nahraďte správnou formou e-mailu">info [zavináč] opengeolabs [tečka] cz</abbr>.\n            Souhlas bude automaticky prodloužen vždy o další roční období, pokud nedojde k jeho odvolání\n            písemnou formou. Jsem si vědom/a svých práv, které subjektům poskytuje\n            zákon č. 101/2000 Sb., o ochraně osobních údajů. Vaše data budou použita\n            pro potřeby organizace kurzů GISMentors.</p>', verbose_name='Ochrana osobních údajů'),
        ),
        migrations.AlterField(
            model_name='attendee',
            name='marketing',
            field=models.BooleanField(help_text='<p>Souhlasím s tím, že společnost <a\n            href="http://opengeolabs.cz" target="_blank">OpenGeoLabs s.r.o.</a> může využít můj\n            e-mail pro zasílání krátkých marketingových zpráv (ne častěji než jednou za\n            měsíc) obsahujících nabídky a slevy kurzů a informace o aktuálním dění ve\n            společnosti.</p>\n            <p>Jsem si vědom/a toho, že souhlas s použitím mého e-mailu pro\n            marketingové účely mohu kdykoliv odvolat zasláním e-mailu na adresu\n            <abbr title="nahraďte správnou formou e-mailu">info [zavináč] opengeolabs [tečka] cz</abbr>. Souhlas bude\n            automaticky prodloužen vždy o další roční období, pokud nedojde k jeho\n            odvolání písemnou formou.</p>\n            ', verbose_name='Marketingová sdělení'),
        ),
        migrations.AlterField(
            model_name='courseattendee',
            name='note',
            field=models.TextField(blank=True, verbose_name='Poznámka'),
        ),
        migrations.AlterField(
            model_name='courseattendee',
            name='token',
            field=models.CharField(default=uuid.UUID('411cecbc-f292-4be9-aced-0d90f6434957'), max_length=255, verbose_name='Token'),
        ),

        migrations.AlterField(
            model_name='attendee',
            name='token',
            field=models.CharField(max_length=255, verbose_name='Token'),
        ),

        migrations.AlterField(
            model_name='courseattendee',
            name='token',
            field=models.CharField(max_length=255, verbose_name='Token'),
        ),
    ]