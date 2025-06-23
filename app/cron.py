
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from app.models import Timetable
from django.conf import settings
import datetime

def Command(BaseCommand):
    

    help = 'Send email reminders to teachers 5 minutes before the start time of their classes.'
    print("===============this is worke==================") 
    def handle(self, *args, **kwargs):
        now = timezone.now()
        reminders = now + datetime.timedelta(minutes=5)
        timetables = Timetable.objects.filter(
            start_time__hour=reminders.hour, 
            start_time__minute=reminders.minute, 
            day_of_week=now.strftime('%A'))

        for timetable in timetables:
            subject = 'Class Reminder'
            message = f'Dear {timetable.teacher.user.name},\n\nThis is a reminder that you have a class for {timetable.subject.subject} with {timetable.school_class.class_name} starting at {timetable.start_time}.\n\nBest regards,\nYour School'
            recipint_list = [timetable.teacher.user.email]
            send_mail(subject, message,  settings.EMAIL_HOST, recipint_list)
            self.stdout.write(self.style.SUCCESS(f'Email sent to {timetable.teacher.email} for class at {timetable.start_time}'))