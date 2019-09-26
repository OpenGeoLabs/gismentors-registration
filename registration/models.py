from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models as gismodels
import uuid
from django.conf import settings
from django.utils.safestring import mark_safe
import datetime
import os

VAT=1.21


class Lector(models.Model):
    class Meta:
        verbose_name = _("Školitel")
        verbose_name_plural = _("Školitelé")

    name = models.CharField(
        max_length=256,
        verbose_name=_("Lector name")
    )

    def __str__(self):
        return self.name


def call_logo_path(instance, filename):
    return instance.logo_path(filename)


class CourseType(models.Model):
    class Meta:
        verbose_name = _("Typ kurzu")
        verbose_name_plural = _("Typy kurzů")

    title = models.CharField(
            max_length=50,
            verbose_name=_("Název"))

    image = models.ImageField(
            upload_to=call_logo_path,
            max_length=256,
            verbose_name=_("Logo"))

    level_choices = (
            (0, _("Začátečník")),
            (1, _("Pokročilý")),
    )

    level = models.IntegerField(
            verbose_name=_("Úroveň"),
            null=True,
            blank=True,
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

    certificate_content = models.TextField(
            verbose_name=_("Obsah certifikátu"),
            default="",
            help_text=_("Každá položka na nový řádek"),
    )

    @property
    def long_str(self):


        if self.level is not None:
            level = dict(self.level_choices)[self.level]
            return "{} - {}".format(self.title, level)
        else:
            return self.title

    def logo_path(self, filename):

        os.umask(0)
        path = "registration/coursetype/"
        complete_path = os.path.join(settings.MEDIA_ROOT, path)
        if settings.DEFAULT_FILE_STORAGE == "django.core.files.storage.FileSystemStorage":
            if not os.path.exists(complete_path):
                os.makedirs(complete_path, 0o777)
        print("get_logo_path", os.path.join(path, filename))
        return os.path.join(path, filename)

    def __str__(self):

        if self.level is not None:
            level = dict(self.level_choices)[self.level][0:3]
            return "{} - {}.".format(self.title, level)
        else:
            return self.title


class Location(models.Model):

    class Meta:
        verbose_name = _("Místo konání")
        verbose_name_plural = _("Místa konání")

    organisation = models.CharField(
            default="",
            max_length=50)

    street = models.CharField(
            default="",
            max_length=50)

    city = models.CharField(
            default="",
            max_length=50)

    postal_code = models.CharField(
            default="",
            max_length=10)

    coordinates = gismodels.PointField(
            verbose_name=_("Souřadnice")
    )

    note = models.TextField(
            blank=True,
            verbose_name=_("Poznámka")
    )

    @property
    def x(self):
        return str(self.coordinates.x)

    @property
    def y(self):
        return str(self.coordinates.y)

    def __str__(self):
        return "{organisation}, {city}".format(organisation=self.organisation,
                                                city=self.city)


class CourseEvent(models.Model):

    class Meta:
        verbose_name = _("Kurz")
        verbose_name_plural = _("Kurzy")

    course_type = models.ForeignKey(
            CourseType,
            on_delete=models.DO_NOTHING)

    CREATED = "created"
    PUBLISHED = "published"
    CLOSED = "closed"
    DECLINED = "declined"
    PAST = "past"

    status_choices = (
        (CREATED, "Vytvořený"),
        (PUBLISHED, "Publikovaný"),
        (CLOSED, "Uzavřený"),
        (DECLINED, "Zrušený"),
        (PAST, "Uplynulý"),
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
                    <dt>Uplynulý</dt>
                    <dd>Kurz již proběhl - neukazuje se v naší veřejné nabídce kurzů.</dd>
                    </dl>
                                """)
    )

    date = models.DateField(
            verbose_name=_("Datum")
    )

    early_date = models.DateField(
        blank=True,
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
            help_text=_("""Kč, s DPH <br/>
        <dl>
        <dt>Začátečník</dt><dd> 5000</dd>
        <dt>Pokročilý</dt><dd> 7500</dd>
        </dl>""")
    )

    price_late = models.IntegerField(
            verbose_name="Standardní",
            help_text=_("""Kč, s DPH<br/>
        <dl>
        <dt>Začátečník</dt><dd>6000</dd>
        <dt>Pokročilý</dt><dd>8500</dd>
        </dl>
        """)
    )

    price_student = models.IntegerField(
            verbose_name="Studentská",
            help_text=_("""Kč, s DPH"""),
            default=1500
    )

    lectors = models.ManyToManyField(Lector)

    @property
    def vat_regular(self):
        return int(self.price_regular)

    @property
    def vat_late(self):
        return int(self.price_late)

    @property
    def vat_student(self):
        return int(self.price_student)


    @property
    def json(self):
        return {
            "name": self.course_type.title,
            "date": self.date,
            "level": self.course_type.level
        }

    @property
    def suma_netto(self):
        attendees = CourseAttendee.objects.filter(course=self)
        return int(sum(att.amount for att in attendees)/VAT)


    def save(self, *args, **kwargs):
        if not self.early_date:
            self.early_date = self.date - datetime.timedelta(16)
        return super(CourseEvent, self).save(*args, **kwargs)

    def __str2__(self):
        return "{}-{}".format(self.course_type.title, self.date)

    def __str__(self):
        return "{} ({})".format(
            self.course_type.__str__(), self.date)


def call_invoice_path(instance, filename):
    return instance.invoice_path(filename)


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

    order = models.CharField(
            null=True,
            blank=True,
            max_length=16,
            verbose_name=_("Číslo objednávky"))

    email = models.EmailField(
            verbose_name=_("Kontaktní e-mail"))

    invoice = models.FileField(
            blank=True,
            max_length=256,
            upload_to=call_invoice_path,
            verbose_name=_("Faktura"))

    note = models.TextField(
            blank=True,
            verbose_name=_("Poznámka"))

    uuid = models.TextField(
            blank=True,
            verbose_name=_("UUID"),
            default="")

    @property
    def amount(self):
        """Count sum of all course_attendees
        """

        attendees = CourseAttendee.objects.filter(invoice_detail=self)
        amount = sum([att.amount for att in attendees])

        return amount

    @property
    def attendee_notes(self):
        """Note from all attendees
        """

        attendees = CourseAttendee.objects.filter(invoice_detail=self)
        notes = [att.note for att in attendees]

        return "\n".join(notes)

    @property
    def text(self):
        """Get list of all courses
        """

        # invoice_text = "{} - {} {}".format(course_event.course_type.title,
        #                                level, course_event.date)
        attendees = CourseAttendee.objects.filter(invoice_detail=self)
        courses = set(
            "{} - {}".format(
                att.course.course_type.long_str,
                att.course.date.strftime("%d.%m.%Y")
            )
            for att in attendees
        )
        return ", ".join(courses)

    def __str__(self):
        if self.name is None:
            str(self.id)
        else:
            return self.name

    def invoice_path(self, filename):

        os.umask(0)
        path = "registration/invoices/{uuid}/".format(uuid=self.uuid)
        complete_path = os.path.join(settings.MEDIA_ROOT, path)
        if settings.DEFAULT_FILE_STORAGE == "django.core.files.storage.FileSystemStorage":
            if not os.path.exists(complete_path):
                os.makedirs(complete_path, 0o777)
        return os.path.join(path, filename)

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        return super(InvoiceDetail, self).save(*args, **kwargs)


class Attendee(models.Model):
    class Meta:
        verbose_name = _("Účastník")
        verbose_name_plural = _("Účastníci")

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

    gdpr_label = "Ochrana osobních údajů"

    gdpr_text = mark_safe("""<p>
            Souhlasím se zpracováním poskytnutých osobních údajů a
            zařazením do databáze uživatelů společnosti <a
                    href="http://opengeolabs.cz" target="_blank">OpenGeoLabs s.r.o.</a> se
            sídlem Brandlova 1559/7, Praha 11, 149 00 (dále jen OpenGeoLabs
            s.r.o.) pro vlastní použití v souladu s příslušnými ustanoveními zákona
            č. 101/2000 Sb., o ochraně osobních údajů a o změně některých údajů v
            platném znění. Beru na vědomí, že údaje budou využívány pouze v rámci
            společnosti OpenGeoLabs s.r.o.</p>
            <p>Jsem si vědom/a toho, že souhlas s
            jejich zpracováním mohu kdykoliv odvolat zasláním e-mailu na adresu
            <abbr title="nahraďte správnou formou e-mailu">info [zavináč] opengeolabs [tečka] cz</abbr>.
            Souhlas bude automaticky prodloužen vždy o další roční období, pokud nedojde k jeho odvolání
            písemnou formou. Jsem si vědom/a svých práv, které subjektům poskytuje
            zákon č. 101/2000 Sb., o ochraně osobních údajů. Vaše data budou použita
            pro potřeby organizace kurzů GISMentors.</p>""")

    gdpr = models.BooleanField(
            verbose_name=gdpr_label,
            help_text=gdpr_text)

    marketing_label = "Marketingová sdělení"

    marketing_text = mark_safe("""<p>Souhlasím s tím, že společnost <a
            href="http://opengeolabs.cz" target="_blank">OpenGeoLabs s.r.o.</a> může využít můj
            e-mail pro zasílání krátkých marketingových zpráv (ne častěji než jednou za
            měsíc) obsahujících nabídky a slevy kurzů a informace o aktuálním dění ve
            společnosti.</p>
            <p>Jsem si vědom/a toho, že souhlas s použitím mého e-mailu pro
            marketingové účely mohu kdykoliv odvolat zasláním e-mailu na adresu
            <abbr title="nahraďte správnou formou e-mailu">info [zavináč] opengeolabs [tečka] cz</abbr>. Souhlas bude
            automaticky prodloužen vždy o další roční období, pokud nedojde k jeho
            odvolání písemnou formou.</p>
            """)

    marketing = models.BooleanField(
            verbose_name=marketing_label,
            help_text=marketing_text)

    date_signed = models.DateField(
            auto_now=True)

    token = models.CharField(
        max_length=255,
        verbose_name=_("Token"))


    def __str__(self):
        return self.name


class CourseAttendee(models.Model):
    class Meta:
        verbose_name = _("Účast na kurzu")
        verbose_name_plural = _("Účasti na kurzech")

    attendee = models.ForeignKey(
            "Attendee",
            on_delete=models.CASCADE
            )

    registration_date = models.DateField(
        verbose_name=_("Datum přihlášení")
    )

    course = models.ForeignKey(
            CourseEvent,
            verbose_name=_("Kurz"),
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
            blank=True,
            verbose_name=_("Poznámka"))

    topics = models.TextField(
            blank=True,
            verbose_name=_("Témata kurzu"))

    next_topics = models.TextField(
            blank=True,
            verbose_name=_("Témata dalších kurzu"))

    token = models.CharField(
        max_length=255,
        verbose_name=_("Token"))

    invoice_detail = models.ForeignKey(
        "InvoiceDetail",
        on_delete=models.PROTECT)

    amount = models.IntegerField(
            verbose_name=_("Částka (s DPH)"))

    attended = models.BooleanField(default=False)


    def __str__(self):
        return self.attendee.name
