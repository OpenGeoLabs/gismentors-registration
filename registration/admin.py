from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import CourseType
from .models import Location
from .models import CourseEvent
from .models import InvoiceDetails
from .models import Attendee
from .models import CourseAttendee
from .models import Address
from .models import Price

# Register your models here.

class AddressInline(admin.StackedInline):
    model=Address

class PriceInline(admin.StackedInline):
    model=Price

class LocationAdmin(LeafletGeoAdmin):
    inlines = (AddressInline, )
    default_zoom = 7
    default_lon = 1730000
    default_lat = 6430000

class AttendeeAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "date_signed")
    readonly_fields=('courses',)

class CourseAdmin(admin.ModelAdmin):
    inlines = (PriceInline, )
    list_display = ("course_type", "date", "attendees")

    def attendees(self, course_event):
        return course_event.courseattendee_set.count()

class CourseAttendeeAdmin(admin.ModelAdmin):
    list_display = ("attendee", "course", "student", "level", "invoice", "certificate")

    def attendee(self, course_event):
        return course_event.attendee.name

class InvoiceDetailsAdmin(admin.ModelAdmin):
    list_display = ("attendee", "course", "student", "invoice")

    def attendee(self, invoice_detail):
        return invoice_detail.course_attendee.attendee.name

    def course(self, invoice_detail):
        return invoice_detail.course_attendee.course.course_type.title

    def student(self, invoice_detail):
        return invoice_detail.course_attendee.student

    def invoice(self, invoice_detail):
        return invoice_detail.course_attendee.student


admin.site.register(CourseType)
admin.site.register(Location, LocationAdmin)
admin.site.register(CourseEvent, CourseAdmin)
admin.site.register(InvoiceDetails, InvoiceDetailsAdmin)
admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(CourseAttendee, CourseAttendeeAdmin)
admin.site.register(Price)
