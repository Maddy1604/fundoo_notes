from celery import Celery
from settings import settings
from user_services.email import send_verification_email, send_reminder_email
from asgiref.sync import async_to_sync
from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry as Task
from datetime import datetime 
from pytz import timezone

celery = Celery(__name__, 
                broker= settings.CELERY_PATH, 
                redbeat_redis_url = settings.REDBEAT_URL, 
                broker_connection_retry_on_startup = True,
                redbeat_lock_key=None,
                beat_max_loop_interval=10,
                beat_scheduler='redbeat.schedulers.RedBeatScheduler')

@celery.task
def send_mail(email, verfit_link):
    async_to_sync(send_verification_email)(email, verfit_link)
    return "Success"
@celery.task
def reminder_email(email, note_id, note_title):
    async_to_sync(send_reminder_email)(email, note_id, note_title)
    return "Success"

# def reminder_schedule(note):
#     task_id = f"reminder_{note.id}"
#     schedule_time = note.reminder.astimezone(pytz.UTC)

#     # Remove existing task if updating
#     celery.control.revoke(task_id, terminate=True)

#     task = Task(name=f'{note_title["title"]}',
#                         task='core.tasks.send_mail',
#                         schedule=crontab(month_of_year=reminder.month,
#                                          day_of_month=reminder.day,
#                                          hour=reminder.hour,
#                                          minute=reminder.minute),
#                         app=celery, args=[])