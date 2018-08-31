from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import CourseType
from .models import Location
from .models import CourseEvent
from .models import InvoiceDetail
from .models import Attendee
from .models import CourseAttendee
from .models import Address


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


class AttendeeAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "date_signed")
    readonly_fields = ('courses',)


class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_type", "date", "attendees")

    def attendees(self, course_event):
        return course_event.courseattendee_set.count()


class CourseAttendeeAdmin(admin.ModelAdmin):
    list_display = ("attendee", "course", "student", "level", "certificate")

    def attendee(self, course_event):
        return course_event.attendee.name


class InvoiceDetailAdmin(admin.ModelAdmin):
    list_display = ("organisation", "invoice")
    inlines = (CourseAttendeeInline, )

    def organisation(self, invoice_detail):
        return invoice_detail.name

    def invoice(self, invoice_detail):
        return invoice_detail.invoice


admin.site.register(CourseType)
admin.site.register(Location, LocationAdmin)
admin.site.register(CourseEvent, CourseAdmin)
admin.site.register(InvoiceDetail, InvoiceDetailAdmin)
admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(CourseAttendee, CourseAttendeeAdmin)
