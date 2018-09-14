from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models as gismodels
import uuid
from django.conf import settings
from django.utils.safestring import mark_safe


VAT=1.21

class CourseType(models.Model):
    class Meta:
        verbose_name = _("Typ školení")
        verbose_name_plural = _("Typ školení")

    title = models.CharField(
            max_length=50,
            verbose_name=_("Název"))

    image = models.ImageField(
            verbose_name=_("Logo"))

    level_choices = (
            (0, _("Začátečník")),
            (1, _("Pokročilý")),
    )

    level = models.IntegerField(
            verbose_name=_("Úroveň"),
            choices=level_choices)

    description = models.TextField(
            verbose_name=_("Popis")
    )

    materials = models.URLField(
            verbose_name=_("Materiály")
    )

    detail = models.URLField(
            verbose_name=_("Detailní link")
    )

    schedule = models.URLField(
            verbose_name=_("Rozvrh")
    )

    def __str__(self):

        level = dict(self.level_choices)[self.level][0:3]
        return "{} - {}.".format(self.title, level)


class Address(models.Model):

    organisation = models.CharField(
            max_length=50)

    street = models.CharField(
            max_length=50)

    city = models.CharField(
            max_length=50)

    postal_code = models.CharField(
            max_length=10)

    location = models.OneToOneField("Location",
            on_delete=models.CASCADE
            )

class Location(models.Model):
    class Meta:
        verbose_name = _("Místo konání")
        verbose_name_plural = _("Místa konání")

    coordinates = gismodels.PointField(
            verbose_name=_("Souřadnice")
    )

    note = models.TextField(
            blank=True,
            verbose_name=_("Poznámka")
    )

    def __str__(self):
        return self.address.organisation


class CourseEvent(models.Model):

    class Meta:
        verbose_name = _("Školení")
        verbose_name_plural = _("Školení")

    course_type = models.ForeignKey(
            CourseType,
            on_delete=models.DO_NOTHING)

    CREATED = "created"
    PUBLISHED = "published"
    CLOSED = "closed"
    DECLINED = "declined"

    status_choices = (
        (CREATED, "Vytvořený"),
        (PUBLISHED, "Publikovaný"),
        (CLOSED, "Uzavřený"),
        (DECLINED, "Zrušený"),
    )

    status = models.CharField(
        max_length=10, choices=status_choices, default=CREATED,
        help_text=_("""<dl>
                    <dt>Vytvořený</dt>
                    <dd>Kurz je vytvořený, ale v nabídce se ještě neukazuje</dd>
                    <dt>Publikovaný</dt>
                    <dd>Kurz se ukazuje v naší veřejné nabídce kurzů</dd>
                    <dt>Uzavřený</dt>
                    <dd>Kurz se ukazuje v naší veřejné nabídce kurzů, ale jako
                    uzavřený pro přihlášky.</dd>
                    <dt>Zrušený</dt>
                    <dd>Kurz se ukazuje v naší nabídce kurzů, ale označený jako
                    zrušený.</dd>
                    </dl>
                                """)
    )

    date = models.DateField(
            verbose_name=_("Datum")
    )

    early_date = models.DateField(
            verbose_name=_("Včasná registrace")
    )

    location = models.ForeignKey(
            Location,
            on_delete=models.CASCADE,
            verbose_name=_("Místo konání")
    )

    note = models.TextField(
        blank=True,
        verbose_name=_("Poznámka ke kurzu")
    )

    price_regular = models.IntegerField(
            verbose_name="Včasná registrace",
            help_text=_("""Kč, bez DPH <br/>
        <dl>
        <dt>Začátečník</dt><dd> 4000</dd>
        <dt>Pokročilý</dt><dd> 6000</dd>
        </dl>""")
    )

    price_late = models.IntegerField(
            verbose_name="Standardní",
            help_text=_("""Kč, bez DPH<br />
        <dl>
        <dt>Začátečník</dt><dd>6000</dd>
        <dt>Pokročilý</dt><dd>7000</dd>
        </dl>
        """)
    )

    price_student = models.IntegerField(
            verbose_name="Studentská",
            help_text=_("""Kč, bez DPH"""),
            default=1000
    )

    @property
    def vat_regular(self):
        global VAT
        return int(VAT*self.price_regular)

    @property
    def vat_late(self):
        return int(VAT*self.price_late)

    @property
    def vat_student(self):
        return int(VAT*self.price_student)

    @property
    def json(self):
        return {
            "name": self.course_type.title,
            "date": self.date,
            "level": self.course_type.level
        }

    def __str__(self):
        return "{} ({})".format(
            self.course_type.__str__(), self.date)


class InvoiceDetail(models.Model):
    class Meta:
        verbose_name = _("Faktura")
        verbose_name_plural = _("Faktury")

    address = models.TextField(
            verbose_name=_("Fakturační adresa"))

    name = models.CharField(
            null=True,
            blank=True,
            max_length=64,
            verbose_name=_("Název organizace"))

    ico = models.CharField(
            null=True,
            blank=True,
            max_length=12,
            verbose_name=_("IČ"))

    dic = models.CharField(
            null=True,
            blank=True,
            max_length=16,
            verbose_name=_("DIČ"))

    objednavka = models.CharField(
            null=True,
            blank=True,
            max_length=16,
            verbose_name=_("Číslo objednávky"))

    email = models.EmailField(
            verbose_name=_("Kontaktní e-mail"))

    amount = models.EmailField(
            verbose_name=_("Částka"), help_text="Částka bez DPH")

    invoice = models.FileField(
            blank=True,
            verbose_name=_("Faktura"))

    text = models.TextField(
            verbose_name=_("Obsah"))

    def __str__(self):
        if self.name == None:
            str(self.id)
        else:
            return self.name


class Attendee(models.Model):
    class Meta:
        verbose_name = _("Učastník")
        verbose_name_plural = _("Učastníci")

    name = models.CharField(
        max_length=50,
        verbose_name=_("Jméno")
    )

    email = models.EmailField(
            primary_key=True,
            verbose_name=_("E-mail účastníka"))

    courses = models.ManyToManyField(
            CourseEvent,
            blank=True)

    gdpr = models.BooleanField(
            verbose_name=_("Souhlas se zpracováním osobních údajů"),
            help_text=_("""Souhlasím se zpracováním poskytnutých osobních údajů
            a zařazením do databáze uživatelů společnosti OpenGeoLabs s.r.o.
            se sídlem v Brandlova 1559/7, Praha 11, 149 00 (dále jen
            OpenGeoLabs s.r.o.) pro vlastní použití v souladu s příslušnými
            ustanoveními zákona č. 101 / 2000 Sb. O ochraně osobních údajů a o
            změně některých údajů v platném znění. Beru na vědomí, že údaje
            budou využívány pouze v rámci společnosti OpenGeoLabs s.r.o.. Jsem
            si vědom/a toho, že souhlas s jejich zpracováním mohu kdykoliv
            odvolat zasláním e-mailu na adresu info [zavináč] opengeolabs
            [tečka] cz. Souhlas bude automaticky prodloužen vždy o další roční
            období, pokud nedojde k jeho odvolání písemnou formou. Jsem si
            vědom/a svých práv, které subjektům poskytuje zákon 101/2000 Sb., o
            ochraně osobních údajů. Vaše data budou použita pro potřeby
            organizace školení GISMentors.
            """))

    marketing = models.BooleanField(
            verbose_name=_("Souhlas s posíláním marketingových materiálů"),
            help_text=_("""Souhlasím s tím, že společnost OpenGeoLabs s.r.o.
            může využít můj e-mail pro zaslání krátké marketingové zprávy (ne
            častěji, než čtyřikrát za rok), obsahující informace o slevách a
            mimořádných nabídkách a informace o aktuálním dění ve společnosti.
            Jsem si vědom/a toho, že souhlas použití mého e-mailu
            pro marketingové účely mohu kdykoliv odvolat zasláním
            e-mailu na adresu info [zavináč] opengeolabs [tečka]
            cz. Souhlas bude automaticky prodloužen vždy o další
            roční období, pokud nedojde k jeho odvolání písemnou
            formou. Jsem si vědom/a svých práv, které subjektům
            poskytuje zákon 101/2000 Sb., o ochraně osobních údajů.
            Na základě tohoto souhlasu budeme zpracovávat vaše
            kontaktní údaje, údaje o absolvovaných kurzech u nás.
            """))

    date_signed = models.DateField(
            auto_now=True)

    def __str__(self):
        return self.name


class CourseAttendee(models.Model):
    class Meta:
        verbose_name = _("Učastník kurzu")
        verbose_name_plural = _("Učastníci kurzu")

    attendee = models.ForeignKey(
            "Attendee",
            on_delete=models.CASCADE
            )

    registration_date = models.DateField(
        verbose_name=_("Datum přihlášení")
    )

    course = models.ForeignKey(
            CourseEvent,
            on_delete=models.PROTECT)

    student = models.BooleanField(
            verbose_name=_("Student"))

    level_choices = (
                (0, "Začátečník"),
                (1, "Mírně pokročilý"),
                (2, "Běžně pracuji s nástroji GIS"),
                (3, "GIS profesionál"),
            )

    level = models.IntegerField(
            verbose_name=_("Úroveň"),
            choices=level_choices)

    note = models.TextField(
            verbose_name=_("Poznámka"))

    topics = models.TextField(
            blank=True,
            verbose_name=_("Témata kurzu"))

    next_topics = models.TextField(
            blank=True,
            verbose_name=_("Témata dalších kurzu"))

    certificate = models.FileField(
            blank=True,
            verbose_name=_("Certifikát"))

    token = models.CharField(
        max_length=255,
        default=uuid.uuid4(),
        verbose_name=_("Token"))

    invoice_detail = models.ForeignKey(
        "InvoiceDetail",
        on_delete=models.PROTECT)


    def __str__(self):
        return self.attendee.name
