from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader

import datetime

from .models import CourseType
from .models import CourseEvent
from .models import Attendee
from .models import CourseAttendee

# Create your views here.

def courses(request):
    latest_courses_list = CourseEvent.objects.order_by('date')[:5]
    context = {
        'latest_courses_list': latest_courses_list,
        "level_choices": CourseType.level_choices
    }
    return render(request, "courses.html", context)

def course(request, course_id):
    course = get_object_or_404(CourseEvent, pk=course_id)
    level_options = course.course_type.level_choices
    context = {
            "course": course,
            "level_options": level_options, 
            "level": course.course_type.level_choices[course.course_type.level][1]
            }
    return render(request, "course.html", context)

def submit(request, course_id):

    attendee = None
    course_attendee = None
    course = get_object_or_404(CourseEvent, pk=course_id)

    found_attendes = Attendee.objects.filter(email=request.POST["email_attendee"])

    if "gdpr" in request.POST and request.POST["gdpr"] == on:
        gdpr = True
    else:
        raise Exception("GDPR musí být odsouhlaseno")

    if found_attendes:
        found_attendes[0].name=request.POST["name"]
        found_attendes[0].date_signed=datetime.date.today()
        found_attendes[0].save()
        attendee = found_attendes[0]
        course_attendees = CourseAttendee.objects.filter(attendee = attendee)
        if course_attendees:
            course_attendee = course_attendees[0]
    else:
        if "marketing" in request.POST and request.POST["marketing"] == on:
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
                course=course,
                student=student,
                level=request.POST["level"],
                note=request.POST["note"],
                topics=request.POST["temata"],
                next_topics=request.POST["temata_next"],
                token=request.POST["csrfmiddlewaretoken"]
        )
        course_attendee.save()


    context = {
            "course_name":course.course_type.title,
            "course_date":course.date
    }


    return render(request, "submitted.html", context)
