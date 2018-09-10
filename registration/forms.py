from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from .models import CourseType
from .models import CourseAttendee
from captcha.fields import CaptchaField


class RegistrationForm(forms.Form):

    captcha = CaptchaField(help_text="Opiště text na obrázku")

    name = forms.CharField(
        label=_('Jméno a příjmení'), max_length=100)

    email_attendee = forms.EmailField(
        label=_('E-mail účastníka'),
        help_text='''Prostřednictvím tohoto e-mailu s Vámi
                     budeme řešit organizační záležitosti kurzu.''')

    organisation = forms.CharField(
        required=False, label=_('Organizace'))

    street = forms.CharField(label=_('Ulice a číslo popisné'))

    city = forms.CharField(label=_('Město'))

    zip_code = forms.CharField(label=_('PSČ'))

    ico = forms.CharField(label=_('IČ'), required=False)

    dic = forms.CharField(label=_('DIČ'), required=False)

    order = forms.CharField(label=_('Číslo objednávky'), required=False)

    invoicemail = forms.EmailField(
        label=_('Fakturační e-mail'), required=False,
        help_text="Pokud se liší od e-mailu účastníka")

    student = forms.BooleanField(
        required=False,
        label=_('Student'),
        help_text="Prohlašuji čestně, že jsem student zapsaný v denním studijním programu.")

    level = forms.ChoiceField(
        label=_('V oblasti GIS se považuji za'),
        choices=CourseAttendee.level_choices
    )

    topics = forms.CharField(
        label=_('Témata na tento kurz'), required=False,
        help_text="Máte nějaké téma, které byste rádi na kurzu probrali?")

    next_topics = forms.CharField(
        label=_('Témata na další kurzy'), required=False,
        help_text="Zajímá Vás nějaký širší okruh, na který jsme zatím nevypsali školení?")

    note = forms.CharField(
        label=_('Poznámka pro organizátory'), required=False,
        help_text="Cokoliv nám chcete sdělit")

    gdpr = forms.BooleanField(
        label="Ochrana osobních údajů",
        help_text="""Souhlasím se zpracováním poskytnutých osobních údajů a
        zařazením do databáze uživatelů společnosti OpenGeoLabs s.r.o. se
        sídlem v Brandlova 1559/7, Praha 11, 149 00 (dále jen OpenGeoLabs
        s.r.o.) pro vlastní použití v souladu s příslušnými ustanoveními zákona
        c. 101 / 2000 Sb. O ochraně osobních údajů a o změně některých údajů v
        platném znění. Beru na vědomí, že údaje budou využívány pouze v rámci
        společnosti OpenGeoLabs s.r.o.. Jsem si vědom/a toho, že souhlas s
        jejich zpracováním mohu kdykoliv odvolat zasláním e-mailu na adresu
        info [zavináč] opengeolabs [tečka] cz. Souhlas bude automaticky
        prodloužen vždy o další roční období, pokud nedojde k jeho odvolání
        písemnou formou. Jsem si vědom/a svých práv, které subjektům poskytuje
        zákon 101/2000 Sb., o ochraně osobních údajů. Vaše data budou použita
        pro potřeby organizace školení GISMentors.""")

    marketing = forms.BooleanField(
        required=False,
        label="Marketingová sdělení",
        help_text=mark_safe('''Souhlasím s tím, že společnost <a
        href="http://opengeolabs.cz">OpenGeoLabs s.r.o.</a> může využít můj
        e-mail pro zaslání krátké marketingové zprávy (ne častěji, než
        čtyřikrát za rok), obsahující informace o aktuálním dění ve
        společnosti. Jsem si vědom/a toho, že souhlas použití mého e-mailu pro
        marketingové účely mohu kdykoliv odvolat zasláním e-mailu na adresu
        <abbr title="nahradtě správnou formou e-mailu">info [zavináč] opengeolabs [tečka] cz</abbr>. Souhlas bude
        automaticky prodloužen vždy o další roční období, pokud nedojde k jeho
        odvolání písemnou formou. Jsem si vědom/a svých práv, které subjektům
        poskytuje zákon 101/2000 Sb., o ochraně osobních údajů. Na základě
        tohoto souhlasu budeme zpracovávat vaše kontaktní údaje, údaje o
        obsolvovaných kurzech u nás.'''))

    contact_fieldset = (name, email_attendee)
