from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.template.loader import render_to_string

import datetime
import uuid
import tempfile
import os
import zipfile
from shutil import copyfile

from registration import utils

from .models import VAT
from .models import CourseType
from .models import CourseEvent
from .models import Attendee
from .models import CourseAttendee
from .models import InvoiceDetail
from .forms import RegistrationForm

from certifikat import generate_certificate


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

    latest_courses_list = CourseEvent.objects.exclude(status=CourseEvent.CREATED).filter(date__gt=datetime.date.today()).order_by('date')

    if request.GET.get("env") == settings.TEST_KEY:
        latest_courses_list = latest_courses_list.filter(course_type__title__contains=settings.TEST_TITLE)
    else:
        latest_courses_list = latest_courses_list.exclude(course_type__title__contains=settings.TEST_TITLE)

    context = {
        'latest_courses_list': latest_courses_list,
        "level_choices": CourseType.level_choices
    }
    return render(request, "courses.html", context)


def _empty_form(request, course_id):

    course = get_object_or_404(CourseEvent, pk=course_id)
    test_env = False

    if request.GET.get("env") == settings.TEST_KEY:
        test_env = settings.TEST_KEY

    context = {
        "course": course,
        "level": course.course_type.level_choices[course.course_type.level][1],
        "form": RegistrationForm(),
        "test_env": test_env
    }

    return render(request, "course-forms.html", context)


def _register_new_attendee(request, course_id):

    form = RegistrationForm(request.POST)
    is_test = (request.GET.get("env") == settings.TEST_KEY)

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
            attended=False,
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

    invoice_text = "{} - {} {}".format(course_event.course_type.title,
                                    level, course_event.date)

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

    suma = sum([int(attendee.invoice_detail.amount) for attendee in course_event.courseattendee_set.all()])

    if is_test:

        send_mail(
            '[GISMentors-kurzy] {} - {} {}'.format(
                course_event.course_type.title, level, course_event.date
            ),
            """
            Kurz: {}
            Účastník: {}
            E-mail: {}
            Organizace: {}
            Celkem registrovaných účastníků: {}
            Celkem peněz (bez DPH): {}
            """.format(
                course_event.course_type.title,
                attendee.name,
                attendee.email,
                request.POST["organisation"],
                len(course_event.courseattendee_set.all()),
                suma
            ),
            'info@gismentors.cz',
            [settings.TEST_MAIL],
            fail_silently=True,
        )

    else:

        send_mail(
            '[GISMentors-kurzy] {} - {} {}'.format(
                course_event.course_type.title, level, course_event.date
            ),
            """
            Kurz: {}
            Účastník: {}
            E-mail: {}
            Organizace: {}
            Celkem registrovaných účastníků: {}
            Celkem peněz (bez DPH): {}
            """.format(
                course_event.course_type.title,
                attendee.name,
                attendee.email,
                request.POST["organisation"],
                len(course_event.courseattendee_set.all()),
                suma
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
            "amount": int(amount*VAT)
        }),
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


def certificates(request, course_id):
    """Generate certificates for given course
    """
    course_event = get_object_or_404(CourseEvent, pk=course_id)

    attendees = course_event.courseattendee_set.all()

    temp_dir = tempfile.mkdtemp(prefix="gismentors-certificates-")
    temp_file = "{}.zip".format(temp_dir)
    os.mkdir(os.path.join(temp_dir, "certs"))
    os.mkdir(os.path.join(temp_dir, "images"))

    certificate_template = utils.get_certificate_template(course_event)
    copyfile(
        course_event.course_type.image.path,
        os.path.join(temp_dir, course_event.course_type.image.name)
    )

    os.chdir(temp_dir)

    with zipfile.ZipFile(temp_file, 'w') as myzip:

        myzip.write(course_event.course_type.image.name)

        for attendee in attendees:
            file_name = generate_certificate.generate(
                certificate_template,
                attendee.attendee.name,
                course_event.date.strftime("%d.%m.%Y"),
                course_event.date.strftime("%d.%m.%Y"),
                "{}-{}-{}.tex".format(
                    course_event.date.strftime("%Y-%m-%d"),
                    course_event.course_type.title,
                    str(attendee.id)
                ),
                course_event.address.city,
                course_event.course_type.image.path
            )

            myzip.write(os.path.basename(file_name))

    with open(temp_file, 'rb') as myzip:
        response = HttpResponse(myzip.read())
        response['Content-Disposition'] = 'attachment; filename={}-{}.zip'.format(
                    course_event.date.strftime("%Y-%m-%d"),
                    course_event.course_type.title
        ),
        response['Content-Type'] = 'application/x-zip'
    return response


