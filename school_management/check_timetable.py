from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app.models import Timetable
from django.core.mail import send_mail  # or any other method for notifications

class Command(BaseCommand):
    help = 'Checks the timetable and sends notifications 5 minutes before class starts'
    print('this====', help) 
    def handle(self, *args, **kwargs):

        
        now = timezone.now()
        upcoming_classes = Timetable.objects.filter(
            start_time__gte=now + timedelta(minutes=5),
            start_time__lte=now + timedelta(minutes=6)  # Check for classes starting in the next minute
        )

        for timetable in upcoming_classes:
            teacher_email = timetable.teacher.email
            subject = f'Upcoming Class: {timetable.subject.subject}'
            message = f'Dear {timetable.teacher},\n\nThis is a reminder that you have a class in {timetable.school_class.class_name} on {timetable.day_of_week} starting at {timetable.start_time}.\n\nBest regards,\nYour School'
            send_mail(subject, message, 'from@example.com', [teacher_email])

        self.stdout.write(self.style.SUCCESS('Successfully checked timetable and sent notifications'))