from django.core.management.base import BaseCommand
from registration.models import CourseEvent
import datetime


class Command(BaseCommand):
    help = 'Set status of CourseEvent according to date'

    def handle(self, *args, **kwargs):

        today = datetime.date.today()

        for evt in CourseEvent.objects.all():

            if (today - evt.date).days == 0:
                evt.status = CourseEvent.PAST
                evt.save()

                self.stdout.write(
                    self.style.SUCCESS('Course {} set status to {}'.format(
                        str(evt), evt.status))
                )
