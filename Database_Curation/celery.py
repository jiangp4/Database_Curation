from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Database_Curation.settings')

app = Celery('Database_Curation')

app.config_from_object('django.conf:settings')
 
# For autodiscover_tasks to work, you must define your tasks in a file called 'tasks.py'.
app.autodiscover_tasks()
 
@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
