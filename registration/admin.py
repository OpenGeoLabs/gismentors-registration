from django.contrib import admin
import datetime
from django.utils.translation import ugettext_lazy as _
from django.db.models.query import QuerySet
from django.http import HttpResponse

from leaflet.admin import LeafletGeoAdmin
import os
import shutil

from .models import CourseType
from .models import CourseEvent
from .models import InvoiceDetail
from .models import Attendee
from .models import CourseAttendee
from .models import Location
from .models import Lector
from .views import get_certificates_zip


class DateFilter(admin.SimpleListFilter):
    """Filter for admin interface of NUTS3 regions (Kraje)
    """
    title = _('Datumy školení (posledních 15)')
    parameter_name = 'date#'

    def lookups(self, request, model_admin):
        course_events = CourseEvent.objects.all().order_by("date")[0:15]
        return (
            (ce.id, "{} - {}".format(ce.course_type.title, ce.date)) for ce in course_events
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val:
            return CourseEvent.objects.filter(pk=val)
        else:
            return CourseEvent.objects.all()


class InvoiceDateFilter(DateFilter):

    def queryset(self, request, queryset):
        val = self.value()
        if val:
            course_event = CourseEvent.objects.get(pk=val)
            return InvoiceDetail.objects.filter(
                courseattendee__course=course_event)
        else:
            return InvoiceDetail.objects.all()


class CourseAttendeeInline(admin.TabularInline):
    model = CourseAttendee

    fields = ("attendee", "student", "attended", "registration_date",
              "amount", "note")
    readonly_fields = ("attendee", "registration_date", "note")
    raw_id_fields = ("invoice_detail",)
    extra = 0



class LocationAdmin(LeafletGeoAdmin):
    default_zoom = 7
    default_lon = 1730000
    default_lat = 6430000


def get_certificates(modeladmin, request, queryset):
    (outzip, tempdir) = get_certificates_zip(queryset[0].id)

    with open(outzip, 'rb') as myzip:
        response = HttpResponse(myzip.read())
        response['Content-Disposition'] = \
            'attachment; filename={}'.format(outzip)
        response['Content-Type'] = 'application/x-zip'
    os.remove(outzip)
    shutil.rmtree(tempdir)
    return response


get_certificates.short_description = _("Stáhnout certifikáty")


class CourseEventAdmin(admin.ModelAdmin):
    inlines = [CourseAttendeeInline]
    list_display = ("course_name", "level", "date", "early_date",
                    "attendees", "days_left", "status", "amount")
    actions = [get_certificates]

    list_filter = (DateFilter, )

    def amount(self, ce):
        attendees = CourseAttendee.objects.filter(course=ce)
        return sum(att.amount for att in attendees)

    def course_name(self, ce):
        return ce.course_type.title

    def level(self, ce):
        return ce.course_type.level_choices[ce.course_type.level][1]

    def attendees(self, ce):
        return len(CourseAttendee.objects.filter(course=ce))

    def days_left(self, ce):
        days = ce.date - datetime.date.today()

        if days.days > 0:
            return days.days
        else:
            return 0


class CourseEventInline(admin.TabularInline):
    model = CourseEvent
    extra = 0


class AttendeeAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "gdpr", "marketing", "date_signed")

    fields = ("name", "email", "courses", "gdpr", "marketing",
              "token")
    readonly_fields = ("token", "date_signed")


class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_type", "date", "attendees")

    def attendees(self, course_event):
        return course_event.course_attendee_set.count()


class CourseAttendeeAdmin(admin.ModelAdmin):
    list_display = ("attendee_name", "attendee_email", "organisation", "student", "course_id",
                    "attended")

    search_fields = ("attendee__name", "attendee__email", "invoice_detail__name")
    list_filter = ("student", )
    raw_id_fields = ("invoice_detail",)
    list_editable = ('attended',)

    def attendee_name(self, ca):
        return ca.attendee.name

    def attendee_email(self, ca):
        return ca.attendee.email

    def organisation(self, ca):
        return ca.invoice_detail.name

    def course_id(self, course_attendee):

        course_date = course_attendee.course.date
        course_name = course_attendee.course.course_type.title
        course_level = course_attendee.course.course_type.level_choices[
                       course_attendee.course.course_type.level][1]
        return "{} - {} {}".format(course_name, course_level, course_date)


class InvoiceDetailAdmin(admin.ModelAdmin):
    list_display = ("organisation", "course_id", "amount", "address", "ico",
                    "dic", "order", "email", "note")
    search_fields = ("name", "order", "email", "ico")

    inlines = (CourseAttendeeInline, )
    list_filter = (InvoiceDateFilter, "order")

    def organisation(self, invoice_detail):
        return invoice_detail.name

    def invoice(self, invoice_detail):
        return invoice_detail.invoice

    def course_id(self, invoice_detail):
        course_attendees = CourseAttendee.objects.filter(invoice_detail=invoice_detail)

        if len(course_attendees) > 0:
            course_date = course_attendees[0].course.date
            course_name = course_attendees[0].course.course_type.title
            course_level = course_attendees[0].course.course_type.level_choices[
                        course_attendees[0].course.course_type.level][1]

            return "{} - {} {}".format(course_name, course_level, course_date)
        else:
            return "No attendee"


    def note(self, invoice_detail):
        course_attendees = CourseAttendee.objects.filter(invoice_detail=invoice_detail)
        notes = ""
        notes = "\n".join([ca.note for ca in course_attendees])
        return notes


admin.site.register(Lector)
admin.site.register(CourseType)
admin.site.register(Location, LocationAdmin)
admin.site.register(CourseEvent, CourseEventAdmin)
admin.site.register(InvoiceDetail, InvoiceDetailAdmin)
admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(CourseAttendee, CourseAttendeeAdmin)
