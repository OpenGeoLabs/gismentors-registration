from django.contrib import admin
import datetime
from django.utils.translation import ugettext_lazy as _

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


class AddressInline(admin.StackedInline):
    model = Address


class CourseAttendeeInline(admin.StackedInline):
    model = CourseAttendee
    fields = ("attendee", )
    readonly_fields = ("attendee", )
    extra = 0


class LocationAdmin(LeafletGeoAdmin):
    inlines = (AddressInline, )
    default_zoom = 7
    default_lon = 1730000
    default_lat = 6430000


class CourseEventAdmin(admin.ModelAdmin):
    inlines = [CourseAttendeeInline]
    list_display = ("course_name", "level", "date", "attendees", "days_left")

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

    #def formfield_for_manytomany(self, db_field, request, **kwargs):
    #    if db_field.name == "courses":
    #        kwargs["queryset"] = /ourseAttendee.objects.filter(owner=request.user)
    #    return super().formfield_for_manytomany(db_field, request, **kwargs)


class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_type", "date", "attendees")

    def attendees(self, course_event):
        return course_event.courseattendee_set.count()


class CourseAttendeeAdmin(admin.ModelAdmin):
    list_display = ("attendee_name", "course_name", "registration_date",
                    "student")

    list_filter = ("course", )

    def attendee_name(self, ca):
        return ca.attendee.name

    def course_name(self, ca):
        return ca.course.course_type


class InvoiceDetailAdmin(admin.ModelAdmin):
    list_display = ("organisation", "invoice")
    inlines = (CourseAttendeeInline, )

    def organisation(self, invoice_detail):
        return invoice_detail.name

    def invoice(self, invoice_detail):
        return invoice_detail.invoice


admin.site.register(CourseType)
admin.site.register(Location, LocationAdmin)
admin.site.register(CourseEvent, CourseEventAdmin)
admin.site.register(InvoiceDetail, InvoiceDetailAdmin)
admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(CourseAttendee, CourseAttendeeAdmin)
