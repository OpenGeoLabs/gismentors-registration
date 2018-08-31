from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.core.mail import send_mail

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

    found_attendes = Attendee.objects.filter(email=request.POST["email_attendee"])

    if "gdpr" in request.POST and request.POST["gdpr"] == "on":
        gdpr = True
    else:
        raise Exception("GDPR musí být odsouhlaseno")

    if found_attendes:
        found_attendes[0].name = request.POST["name"]
        found_attendes[0].date_signed = datetime.date.today()
        found_attendes[0].save()
        attendee = found_attendes[0]
        course_attendees = CourseAttendee.objects.filter(attendee=attendee)
        if course_attendees:
            course_attendee = course_attendees[0]
            attendee.courses.add(course_event)
    else:
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

    if not course_attendee:

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

    name  = request.POST["organisation"]
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
