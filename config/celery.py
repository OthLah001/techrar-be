import os
from celery import Celery
import ssl
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery(
    "config"
) if not settings.IS_LIVE_ENV else Celery(
    "config",
    broker_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
    redis_backend_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE}
)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()