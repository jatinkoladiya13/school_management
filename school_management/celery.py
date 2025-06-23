from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')

app = Celery('school_management')

app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks()
