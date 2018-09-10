from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.template.loader import render_to_string

import datetime

from .models import CourseType
from .models import CourseEvent
from .models import Attendee
from .models import CourseAttendee
from .models import InvoiceDetail
from .forms import RegistrationForm

def courses_json(request):
    latest_courses_list = CourseEvent.objects.order_by('date')
    print([course.json for course in latest_courses_list])
    return JsonResponse({
        "courses": [course.json for course in latest_courses_list if
                    course.date > datetime.date.today()]})

def courses_atom(request):
    latest_courses_list = CourseEvent.objects.order_by('date')
    print([course.json for course in latest_courses_list])
    return JsonResponse({
        "courses": [course.json for course in latest_courses_list if
                    course.date > datetime.date.today()]})


def courses(request):
    latest_courses_list = CourseEvent.objects.order_by('date')
    context = {
        'latest_courses_list': latest_courses_list,
        "level_choices": CourseType.level_choices
    }
    return render(request, "courses.html", context)


def _empty_form(request, course_id):

    course = get_object_or_404(CourseEvent, pk=course_id)
    context = {
        "course": course,
        "level": course.course_type.level_choices[course.course_type.level][1],
        "form": RegistrationForm()
    }

    return render(request, "course-forms.html", context)


def _register_new_attendee(request, course_id):

    form = RegistrationForm(request.POST)

    # Validate the form: the captcha field will automatically
    # check the input
    if not form.is_valid():
        # return defaults.bad_request(request, SuspiciousOperation("Form not valid"))
        pass

    attendee = None
    course_attendee = None
    course_event = get_object_or_404(CourseEvent, pk=course_id)


    if "gdpr" in request.POST and request.POST["gdpr"] == "on":
        gdpr = True
    else:
        pass
        # return defaults.bad_request(request, ValidationError("GDPR musí být potvrzeno"))

    if "marketing" in request.POST and request.POST["marketing"] == "on":
        marketing = True
    else:
        marketing = False

    try:
        attendee = Attendee.objects.get(email=request.POST["email_attendee"])
        attendee.name = request.POST["name"]
        attendee.date_signed = datetime.date.today()
        attendee.marketing = marketing
        attendee.gdpr = gdpr
        attendee.save()
    except ObjectDoesNotExist as e:
        new_attendee = Attendee.objects.create(
                name=request.POST["name"],
                email=request.POST["email_attendee"],
                gdpr=gdpr,
                marketing=marketing,
                date_signed=datetime.date.today())
        new_attendee.save()
        attendee = new_attendee

    if "student" in request.POST and request.POST["student"] == "on":
        student = True
    else:
        student = False

    try:
        existing_attendee = course_event.courseattendee_set.get(
            attendee__name=attendee.name,
            attendee__email=attendee.email)
        context = {
            "name": existing_attendee.attendee.name,
            "title": course_event.course_type.title
        }
        return render(request, "already_registered.html", context)
    except ObjectDoesNotExist as e:
            pass

    course_attendee = CourseAttendee(
            attendee=attendee,
            course=course_event,
            student=student,
            registration_date=datetime.date.today(),
            level=request.POST["level"],
            note=request.POST["note"],
            topics=request.POST["topics"],
            next_topics=request.POST["next_topics"],
            token=request.POST["csrfmiddlewaretoken"]
    )

    attendee.courses.add(course_event)
    attendee.save()

    amount = 0
    if course_attendee.registration_date <= course_event.early_date:
        if course_attendee.student:
            amount = course_event.price_student
        else:
            amount = course_event.price_regular
    else:
        amount = course_event.price_late

    level = list(filter(lambda c: c[0] == course_event.course_type.level,
                 CourseType.level_choices))[0][1]

    invoice_text = "{} - {}".format(course_event.course_type.title,
                                    level)

    name = request.POST["organisation"]
    if not name:
        name = attendee.name
    invoicemail = request.POST["invoicemail"]
    if not invoicemail:
        invoicemail = request.POST["email_attendee"]

    invoice_detail = InvoiceDetail(
        address="{street}\n{zipcode} - {city}".format(
            street=request.POST["street"], zipcode=request.POST["zip_code"],
            city=request.POST["city"]),
        name=name,
        ico=request.POST["ico"],
        dic=request.POST["dic"],
        objednavka=request.POST["order"],
        amount=amount,
        text=invoice_text,
        email=invoicemail
    )

    invoice_detail.save()
    course_attendee.invoice_detail = invoice_detail
    course_attendee.save()

    context = {
            "course_name": course_event.course_type.title,
            "course_date": course_event.date,
            "attendee": attendee.name,
            "course_id": course_event.id
    }

    send_mail(
        '[GISmentors-kurzy] {} - {}'.format(
            course_event.course_type.title, course_event.date
        ),
        """
        Kurz: {}
        Účastník: {}
        Organizace: {}
        Celkem registrovaných účastníků: {}""".format(
            course_event.course_type.title,
            attendee.name,
            invoice_detail.name,
            len(course_event.courseattendee_set.all())
        ),
        'info@gismentors.cz',
        [settings.INFO_MAIL],
        fail_silently=True,
    )

    send_mail(
        '[GISmentors-kurzy] Potvrzení přihlášení',
        render_to_string('potvrzeni.txt', {
            'name': attendee.name,
            "title": course_event.course_type.title,
            "date": course_event.date,
            "student": student}),
        'info@gismentors.cz',
        [attendee.email],
        fail_silently=True,
    )

    return render(request, "submitted.html", context)


def course(request, course_id):

    if request.POST:
        return _register_new_attendee(request, course_id)
    else:
        return _empty_form(request, course_id)
