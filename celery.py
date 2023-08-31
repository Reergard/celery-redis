from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
import logging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FanVerse.settings')


logging.basicConfig(level=logging.INFO)
app = Celery('FanVerse')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_connection_retry_on_startup = True

@app.task
def debug_task():
    print("Debug task executed")


    app.conf.beat_schedule = {
        #'send_abandoned_notification': {
        ##    'task': 'catalog.tasks.send_abandoned_notification',
        #    'schedule': crontab(minute='*/5'),  # Запускать каждый день в полночь (minute=0, hour=0)
        #},

        'update_book_status_and_author': {
            'task': 'catalog.tasks.check_abandoned_books',
            'schedule': crontab(minute='*/1'),  # Запустится каждый час
        },

        'simple_debug_task': {
            'task': 'catalog.tasks.simple_debug_task',
            'schedule': crontab(minute='1'),
        },
    }

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
