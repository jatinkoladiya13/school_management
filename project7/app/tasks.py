from celery import shared_task
from datetime import timedelta
from app.models import Timetable
from datetime import datetime
from django.conf import settings
import smtplib
import dotenv
import os
from datetime import datetime
from datetime import time

dotenv.read_dotenv(dotenv='D:\pythonProject\Projects\project7\project7\.env')

@shared_task
def check_timetable_task():

    now = datetime.now().time()
    five_minutes_from_now = (datetime.now()+ timedelta(minutes=5)).time()
    timetables = Timetable.objects.filter(
        start_time__gte=now,
        start_time__lte=five_minutes_from_now
    )

    auth_email = os.getenv('EMAIL_USER')
    auth_password = os.getenv('EMAIL_PASS')

    for timetable in timetables:
        teacher_email = timetable.teacher.user.email
        message = f'Dear {timetable.teacher},\n\nThis is a reminder that you have a class in {timetable.school_class.class_name} on {timetable.day_of_week} starting at {timetable.start_time}.\n\nBest regards,\nYour School'
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(auth_email, auth_password)
            server.sendmail(auth_email, teacher_email, message)
            print("===========Successfully send email===================")  
    