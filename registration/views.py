from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist

import datetime

from .models import CourseType
from .models import CourseEvent
from .models import Attendee
from .models import CourseAttendee
from .models import InvoiceDetail


def courses(request):
    latest_courses_list = CourseEvent.objects.order_by('date')[:5]
    context = {
        'latest_courses_list': latest_courses_list,
        "level_choices": CourseType.level_choices
    }
    return render(request, "courses.html", context)

def course(request, course_id):
    course = get_object_or_404(CourseEvent, pk=course_id)
    level_options = CourseAttendee.level_choices
    context = {
            "course": course,
            "level_options": level_options,
            "level": course.course_type.level_choices[course.course_type.level][1]
            }
    return render(request, "course.html", context)

def submit(request, course_id):

    attendee = None
    course_attendee = None
    course_event = get_object_or_404(CourseEvent, pk=course_id)


    if "gdpr" in request.POST and request.POST["gdpr"] == "on":
        gdpr = True
    else:
        raise Exception("GDPR musí být odsouhlaseno")

    try:
        attendee = Attendee.objects.get(email=request.POST["email_attendee"])
        attendee.name = request.POST["name"]
        attendee.date_signed = datetime.date.today()
        attendee.save()
    except ObjectDoesNotExist as e:
        if "marketing" in request.POST and request.POST["marketing"] == "on":
            marketing = True
        else:
            marketing = False
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

    course_attendee = CourseAttendee(
            attendee=attendee,
            course=course_event,
            student=student,
            registration_date=datetime.date.today(),
            level=request.POST["level"],
            note=request.POST["note"],
            topics=request.POST["temata"],
            next_topics=request.POST["temata_next"],
            token=request.POST["csrfmiddlewaretoken"]
    )

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
    invoice_detail = InvoiceDetail(
        address="{street}\n{zipcode} - {city}".format(
            street=request.POST["street"], zipcode=request.POST["zip"],
            city=request.POST["city"]),
        name=name,
        ico=request.POST["ico"],
        dic=request.POST["dic"],
        objednavka=request.POST["order"],
        amount=amount,
        text=invoice_text,
        email=request.POST["email"],
    )

    invoice_detail.save()
    course_attendee.invoice_detail = invoice_detail
    course_attendee.save()

    context = {
            "course_name": course_event.course_type.title,
            "course_date": course_event.date
    }

    # TODO: send confirmation mail
    # TODO: send mail to courses@gismentors.cz with information about new
    # registration

    #send_mail(
    #    'Od Djanga',
    #    'Účastník přihlášen',
    #    'jachym@chvostokok',
    #    ['jachym@chvostoskok'],
    #    fail_silently=False,
    #)

    return render(request, "submitted.html", context)
