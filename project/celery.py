"""
Celery configuration for the project.

This module sets up Celery for asynchronous task processing.
Tasks like sending emails are processed in the background using Redis as a message broker.
"""
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Create a Celery app instance
app = Celery('project')

# Load configuration from Django settings with 'CELERY_' prefix
# This allows all Celery settings to be defined in settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks from all installed apps
# Celery will look for tasks.py or any module containing @shared_task decorators
app.autodiscover_tasks()

# IMPORTANT: Explicitly import tasks to ensure they are registered
# This is needed on Windows where autodiscover sometimes fails
from utils import email_tasks  # noqa


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')
