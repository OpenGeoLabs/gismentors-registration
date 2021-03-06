from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.template.loader import render_to_string
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.template.defaultfilters import date as _date

import datetime
import uuid
import tempfile
import os
import pathlib
import zipfile
from shutil import copyfile
import jinja2

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

    latest_courses_list = CourseEvent.objects.exclude(status=CourseEvent.CREATED).filter(date__gt=datetime.date.today()).order_by('date')

    if request.GET.get("env") == settings.TEST_KEY:
        latest_courses_list = latest_courses_list.filter(course_type__title__contains=settings.TEST_TITLE)
    else:
        latest_courses_list = latest_courses_list.exclude(course_type__title__contains=settings.TEST_TITLE)

    context = {
        "latest_courses_list": latest_courses_list,
        "level_choices": CourseType.level_choices,
        "google_tag": settings.GOOGLE_TAG,
    }
    return render(request, "courses.html", context)


def _empty_form(request, course_id):

    course = get_object_or_404(CourseEvent, pk=course_id)
    test_env = False

    if request.GET.get("env") == settings.TEST_KEY:
        test_env = settings.TEST_KEY

    if course.course_type.level is not None:
        level = course.course_type.level_choices[course.course_type.level][1]
    else:
        level = None
    context = {
        "course": course,
        "level": level,
        "form": RegistrationForm(),
        "test_env": test_env,
        "google_tag": settings.GOOGLE_TAG,
    }

    return render(request, "course-forms.html", context)


def _create_new_attende(name, email, gdpr, marketing):
    """Register new generic attendee

    :return: new_attendee
    """

    new_attendee = Attendee.objects.create(
            name=name,
            email=email,
            gdpr=gdpr,
            marketing=marketing,
            token=uuid.uuid1(),
            date_signed=datetime.date.today()
    )
    new_attendee.save()
    return new_attendee


def _update_attendee_by_email(email, marketing, gdpr, name=None):
    """Update attendee marketing information and GDPR of user identified by
    e-mail
    """

    attendee = Attendee.objects.get(email=email)
    attendee.date_signed = datetime.date.today()
    attendee.marketing = marketing
    attendee.gdpr = gdpr
    if name:
        attendee.name = name
    attendee.save()

    return attendee


def _register_new_attendee(request, course_id):
    """Register new attendee person in our database
    """

    form = RegistrationForm(request.POST)
    is_test = (request.GET.get("env") == settings.TEST_KEY)

    # Validate the form: the captcha field will automatically
    # check the input
    if not form.is_valid():
        # return defaults.bad_request(request,
        # SuspiciousOperation("Form not valid"))
        pass

    name = request.POST["name"]
    email = request.POST["email_attendee"]
    attendee = None
    course_attendee = None
    course_event = get_object_or_404(CourseEvent, pk=course_id)
    gdpr = False
    marketing = False
    student = False
    amount = 0

    if course_event.course_type.level is not None:
        level = list(filter(lambda c: c[0] == course_event.course_type.level,
                    CourseType.level_choices))[0][1]
    else:
        level = None

    if "gdpr" in request.POST and request.POST["gdpr"] == "on":
        gdpr = True

    if "marketing" in request.POST and request.POST["marketing"] == "on":
        marketing = True

    if "student" in request.POST and request.POST["student"] == "on":
        student = True
    else:
        student = False

    existing_attendees = course_event.courseattendee_set.filter(
        attendee__email=email
    )

    if level is not None:
        title = "{} - {}".format(course_event.course_type.title, level)
    else:
        title = course_event.course_type.title

    if len(existing_attendees) > 0:
        context = {
            "name": existing_attendees[0].attendee.name,
            "email": existing_attendees[0].attendee.email,
            "title": title,
            "google_tag": settings.GOOGLE_TAG,
        }
        return render(request, "already_registered.html", context)

    # save attendee details only if attendee was registered
    attendee = None
    try:
        attendee = Attendee.objects.get(email=email)
        _update_attendee_by_email(email, marketing, gdpr, name)
    except ObjectDoesNotExist as e:
        attendee = _create_new_attende(name, email, gdpr, marketing)

    amount = 0

    if datetime.date.today() <= course_event.early_date:
        if student:
            amount = course_event.price_student
        else:
            amount = course_event.price_regular
    else:
        amount = course_event.price_late

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
            amount=amount,
            token=uuid.uuid1()
    )

    attendee.courses.add(course_event)

    organisation = request.POST["organisation"]
    if not organisation:
        organisation = attendee.name
    invoicemail = request.POST["invoicemail"]
    if not invoicemail:
        invoicemail = request.POST["email_attendee"]

    order = request.POST["order"]
    invoice_detail = None
    if order:
        invoice_details = InvoiceDetail.objects.filter(
            order=order,
            name=organisation
        )
        if len(invoice_details) > 0:
            invoice_detail = invoice_details[0]

    if not invoice_detail:
        invoice_detail = InvoiceDetail(
            address="{street}\n{zipcode} {city}".format(
                street=request.POST["street"],
                zipcode=request.POST["zip_code"],
                city=request.POST["city"]),
            name=organisation,
            ico=request.POST["ico"],
            dic=request.POST["dic"],
            order=request.POST["order"],
            email=invoicemail
        )

    invoice_detail.save()
    course_attendee.invoice_detail = invoice_detail
    course_attendee.save()

    _send_mails(course_event, attendee, title, organisation, amount, is_test)

    context = {
        "course_name": title,
        "course_date": course_event.date,
        "attendee": attendee.name,
        "mail": attendee.email,
        "course_id": course_event.id,
        "google_tag": settings.GOOGLE_TAG,
    }

    return render(request, "submitted.html", context)


def _send_mails(course_event, attendee, title,
                organisation, amount, is_test=False):
    """Send e-mails to info at gismentors and to new course attendee
    """

    if is_test:

        send_mail(
            '[GISMentors-kurzy] {} {}'.format(title, course_event.date),
            """
            Kurz: {}
            Účastník: {}
            E-mail: {}
            Organizace: {}
            Celkem registrovaných účastníků: {}
            Celkem peněz (bez DPH): {}
            """.format(
                title,
                attendee.name,
                attendee.email,
                organisation,
                len(course_event.courseattendee_set.all()),
                course_event.suma_netto
            ),
            'info@gismentors.cz',
            [settings.TEST_MAIL],
            fail_silently=True,
        )

    else:

        send_mail(
            '[GISMentors-kurzy] {} {}'.format(title, course_event.date),
            """
            Kurz: {}
            Účastník: {}
            E-mail: {}
            Organizace: {}
            Celkem registrovaných účastníků: {}
            Celkem peněz (bez DPH): {}
            """.format(
                title,
                attendee.name,
                attendee.email,
                organisation,
                len(course_event.courseattendee_set.all()),
                course_event.suma_netto
            ),
            'info@gismentors.cz',
            [settings.INFO_MAIL],
            fail_silently=True,
        )

    send_mail(
        '[GISMentors-kurzy] Potvrzení přihlášky',
        render_to_string('potvrzeni.txt', {
            'name': attendee.name,
            "title": title,
            "date": course_event.date,
            "amount": int(amount)
        }),
        'info@gismentors.cz',
        [attendee.email],
        fail_silently=True,
    )


def course(request, course_id):

    course_event = get_object_or_404(CourseEvent, pk=course_id)

    if course_event.date <= datetime.date.today():
        raise Http404("Kurz již proběhl. | The course took already place.")

    if request.POST:
        return _register_new_attendee(request, course_id)
    else:
        return _empty_form(request, course_id)


def get_certificates_zip(course_id):

    course_event = get_object_or_404(CourseEvent, pk=course_id)

    attendees = course_event.courseattendee_set.all()

    temp_dir = tempfile.mkdtemp(prefix="gismentors-certificates-")
    temp_file = "{}-certifikaty.zip".format(course_event.__str2__())
    os.mkdir(os.path.join(temp_dir, "certs"))
    os.mkdir(os.path.join(temp_dir, "images"))

    template = get_template("certificate.tex")
    mydir = str(pathlib.Path(template.origin.name).parent)

    latex_jinja_env = jinja2.Environment(
        block_start_string='\BLOCK{',
        block_end_string='}',
        variable_start_string='\VAR{',
        variable_end_string='}',
        comment_start_string='\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(mydir)
    )

    certificate_template = latex_jinja_env.get_template("certificate.tex")

    copyfile(
        course_event.course_type.image.path,
        os.path.join(temp_dir,
                     os.path.basename(course_event.course_type.image.name))
    )

    os.chdir(temp_dir)
    copyfile(finders.find("logo_labels.png"),
             "logo_labels.png")
    copyfile(finders.find("Makefile"),
             "Makefile")

    content = [l.strip() for l in
               course_event.course_type.certificate_content.split("\n")]

    with zipfile.ZipFile(temp_file, 'w') as myzip:

        myzip.write(os.path.basename(course_event.course_type.image.name))

        for attendee in attendees:

            context = {
                "name": attendee.attendee.name,
                "course_title": course_event.course_type.long_str,
                "logo": course_event.course_type.image.name,
                "place": course_event.location.postal_code,
                "date": _date(course_event.date, "j. E Y"),
                "content": content,
                "lectors": [lector.name for lector in course_event.lectors.all()],
                "detail": course_event.course_type.detail,

            }
            file_name = "{}-{}-{}.tex".format(
                    course_event.date.strftime("%Y-%m-%d"),
                    course_event.course_type.title,
                    str(attendee.id)
                )

            with open(file_name, "w") as out:
                out.write(certificate_template.render(context))

            myzip.write(os.path.basename(file_name))
        myzip.write("logo_labels.png")

        myzip.write("Makefile")

    return (temp_file, temp_dir)


@login_required(login_url='/admin/login/')
def certificates(request, course_id):
    """Generate certificates for given course, save them to ZIP file and return
    back
    """

    course_event = get_object_or_404(CourseEvent, pk=course_id)
    outzip = get_certificates_zip(course_id)
    with open(outzip, 'rb') as myzip:
        response = HttpResponse(myzip.read())
        response['Content-Disposition'] = 'attachment; filename=certifikaty-{}-{}.zip'.format(
                    course_event.date.strftime("%Y-%m-%d"),
                    course_event.course_type.title
        )
        response['Content-Type'] = 'application/x-zip'
    return response


