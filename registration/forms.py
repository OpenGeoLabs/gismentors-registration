from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from .models import CourseType
from .models import CourseAttendee
from .models import Attendee
from captcha.fields import CaptchaField


class RegistrationForm(forms.Form):

    captcha = CaptchaField(help_text="Opište text na obrázku")

    name = forms.CharField(
        label=_('Jméno a příjmení'), max_length=255,
        help_text="""Jméno a příjmení včetně titulů""")

    email_attendee = forms.EmailField(
        label=_('E-mail účastníka'),
        help_text='''Prostřednictvím tohoto e-mailu s Vámi
                     budeme řešit organizační záležitosti kurzu.''')

    organisation = forms.CharField(
        required=False, max_length=100, label=_('Organizace'))

    street = forms.CharField(label=_('Ulice a číslo popisné'),
                             max_length=50)

    city = forms.CharField(label=_('Město'), max_length=50)

    zip_code = forms.CharField(label=_('PSČ'), max_length=10)

    ico = forms.CharField(label=_('IČ'), required=False, max_length=12)

    dic = forms.CharField(label=_('DIČ'), required=False, max_length=16)

    order = forms.CharField(label=_('Číslo objednávky'), required=False,
                            max_length=16)

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
        widget=forms.Textarea,
        help_text="Máte nějaké téma, které byste rádi na kurzu probrali?")

    next_topics = forms.CharField(
        label=_('Témata na další kurzy'), required=False,
        widget=forms.Textarea,
        help_text="Zajímá Vás nějaký širší okruh, na který jsme zatím nevypsali školení?")

    note = forms.CharField(
        label=_('Poznámka pro organizátory'), required=False,
        widget=forms.Textarea,
        help_text="Cokoliv nám chcete sdělit")

    gdpr = forms.BooleanField(
        label=Attendee.gdpr_label,
        help_text=Attendee.gdpr_text)

    marketing = forms.BooleanField(
        required=False,
        label=Attendee.marketing_label,
        help_text=Attendee.marketing_text)

    contact_fieldset = (name, email_attendee)
