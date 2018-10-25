from django.contrib import admin
import datetime
from django.utils.translation import ugettext_lazy as _
from django.db.models.query import QuerySet

from leaflet.admin import LeafletGeoAdmin

from .models import CourseType
from .models import Location
from .models import CourseEvent
from .models import InvoiceDetail
from .models import Attendee
from .models import CourseAttendee
from .models import Address

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


class AddressInline(admin.StackedInline):
    model = Address


class CourseAttendeeInline(admin.TabularInline):
    model = CourseAttendee
    fields = ("attendee", "student", "attended", "registration_date")
    readonly_fields = ("attendee", "registration_date", )
    extra = 0


class LocationAdmin(LeafletGeoAdmin):
    inlines = (AddressInline, )
    default_zoom = 7
    default_lon = 1730000
    default_lat = 6430000


class CourseEventAdmin(admin.ModelAdmin):
    inlines = [CourseAttendeeInline]
    list_display = ("course_name", "level", "status", "date", "attendees", "days_left")

    list_filter = (DateFilter, )

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
    list_display = ("name", "email", "date_signed")

    fields = ("name", "email", "courses", "gdpr", "marketing",
              "token")
    readonly_fields = ("token", "date_signed")


class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_type", "date", "attendees")

    def attendees(self, course_event):
        return course_event.course_attendee_set.count()


class CourseAttendeeAdmin(admin.ModelAdmin):
    list_display = ("attendee_name", "course_id", "registration_date",
                    "student", "attended")

    list_filter = ("course", )
    list_editable = ('attended',)

    def attendee_name(self, ca):
        return ca.attendee.name

    def course_id(self, course_attendee):

        course_date = course_attendee.course.date
        course_name = course_attendee.course.course_type.title
        course_level = course_attendee.course.course_type.level_choices[
                       course_attendee.course.course_type.level][1]
        return "{} - {} {}".format(course_name, course_level, course_date)


class InvoiceDetailAdmin(admin.ModelAdmin):
    list_display = ("organisation", "course_id", "amount", "address", "ico",
                    "dic", "objednavka", "email")

    inlines = (CourseAttendeeInline, )
    list_filter = (InvoiceDateFilter, )

    def organisation(self, invoice_detail):
        return invoice_detail.name

    def invoice(self, invoice_detail):
        return invoice_detail.invoice

    def course_id(self, invoice_detail):
        course_attendee = CourseAttendee.objects.get(invoice_detail=invoice_detail)

        course_date = course_attendee.course.date
        course_name = course_attendee.course.course_type.title
        course_level = course_attendee.course.course_type.level_choices[
                       course_attendee.course.course_type.level][1]
        
        return "{} - {} {}".format(course_name, course_level, course_date)


admin.site.register(CourseType)
admin.site.register(Location, LocationAdmin)
admin.site.register(CourseEvent, CourseEventAdmin)
admin.site.register(InvoiceDetail, InvoiceDetailAdmin)
admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(CourseAttendee, CourseAttendeeAdmin)
