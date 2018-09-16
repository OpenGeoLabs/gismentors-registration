from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.template.loader import render_to_string

import datetime
import uuid

from .models import CourseType
from .models import CourseEvent
from .models import Attendee
from .models import CourseAttendee
from .models import InvoiceDetail
from .forms import RegistrationForm


def courses_json(request):
    latest_courses_list = CourseEvent.objects.order_by('date')
    return JsonResponse({
        "courses": [course.json for course in latest_courses_list if
                    course.date > datetime.date.today()]})


def courses_atom(request):
    latest_courses_list = CourseEvent.objects.order_by('date')
    courses = latest_courses_list
    context = {
        "courses": courses,
        "date": courses[0].date,
        "uuid": uuid.uuid1(),
    }
    return render(request, "atom.xml", context)


def courses(request):
    latest_courses_list = CourseEvent.objects.exclude(status=CourseEvent.CREATED).filter(date__gte=datetime.date.today()).order_by('date')
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

    level = list(filter(lambda c: c[0] == course_event.course_type.level,
                 CourseType.level_choices))[0][1]



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
                token=uuid.uuid1(),
                date_signed=datetime.date.today())
        new_attendee.save()
        attendee = new_attendee

    if "student" in request.POST and request.POST["student"] == "on":
        student = True
    else:
        student = False

    existing_attendees = course_event.courseattendee_set.filter(
        attendee__name=attendee.name,
        attendee__email=attendee.email)

    if len(existing_attendees) > 0:
        context = {
            "name": existing_attendees[0].attendee.name,
            "email": attendee.email,
            "title": "{} - {}".format(course_event.course_type.title, level)
        }
        return render(request, "already_registered.html", context)

    course_attendee = CourseAttendee(
            attendee=attendee,
            course=course_event,
            student=student,
            registration_date=datetime.date.today(),
            level=request.POST["level"],
            note=request.POST["note"],
            topics=request.POST["topics"],
            next_topics=request.POST["next_topics"],
            token=uuid.uuid1()
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
            "course_name": "{} - {}".format(course_event.course_type.title,
                                            level),
            "course_date": course_event.date,
            "attendee": attendee.name,
            "mail": attendee.email,
            "course_id": course_event.id
    }

    send_mail(
        '[GISMentors-kurzy] {} - {} {}'.format(
            course_event.course_type.title, level, course_event.date
        ),
        """
        Kurz: {}
        Účastník: {}
        E-mail: {}
        Organizace: {}
        Celkem registrovaných účastníků: {}""".format(
            course_event.course_type.title,
            attendee.name,
            attendee.email,
            request.POST["organisation"],
            len(course_event.courseattendee_set.all())
        ),
        'info@gismentors.cz',
        [settings.INFO_MAIL],
        fail_silently=True,
    )

    send_mail(
        '[GISMentors-kurzy] Potvrzení přihlášky',
        render_to_string('potvrzeni.txt', {
            'name': attendee.name,
            "title": "{} - {}".format(course_event.course_type.title, level),
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
