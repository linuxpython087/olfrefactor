import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")
app.config_from_object("django.conf:settings", namespace="CELERY")

# 🔥 C'EST ÇA QUI MANQUE
app.autodiscover_tasks()
# app.conf.worker_hijack_root_logger = False
