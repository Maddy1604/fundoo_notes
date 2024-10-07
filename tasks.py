from celery import Celery
from settings import settings
from user_services.email import send_verification_email
from asgiref.sync import async_to_sync

celery = Celery(__name__, broker= settings.CELERY_PATH, broker_connection_retry_on_startup = True)

@celery.task
def send_mail(email, verfit_link):
    async_to_sync(send_verification_email)(email, verfit_link)
    return "success"

