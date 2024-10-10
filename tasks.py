from celery import Celery
from settings import settings
from user_services.email import send_verification_email, send_reminder_email
from asgiref.sync import async_to_sync
from loguru import logger


celery = Celery(__name__, 
                broker= settings.CELERY_PATH, 
                redbeat_redis_url = settings.REDBEAT_URL, 
                broker_connection_retry_on_startup = True,
                redbeat_lock_key=None,
                beat_max_loop_interval=10,
                beat_scheduler='redbeat.schedulers.RedBeatScheduler',
                enable_utc=False,)

@celery.task
def send_mail(email, verfit_link):
    """
    Description:
    This task sends a verification email for a new user.
    Parameters:
    email: The email address of new user 
    verify_link: The verification link for user
    Returns:
    str: A message indicating the result of the email sending operation as success.
    """
    logger.info(f"Sending verification email to user {email}")

    try:
        async_to_sync(send_verification_email)(email, verfit_link)
        logger.info(f"Verification email successfully sent to {email}")
        return "Success"
    except Exception as error:
        # Log any error that occurs
        logger.error(f"Failed to send verification email to {email}: {str(error)}")
        raise ValueError("Falied to perform task")

@celery.task
def reminder_email(email, note_id, note_title):
    """
    Description:
    This task sends a reminder email for a specific note identified by its ID.
    Parameters:
    note_id: The ID of the note for which the reminder email should be sent.
    note_title: The title of note also be send with in email
    Returns:
    str: A message indicating the result of the email sending operation.
    """
    logger.info(f"Starting remainder email task for {email}")
    
    try:
        # Send reminder email
        async_to_sync(send_reminder_email)(email, note_id, note_title)
        logger.info(f"Reminder email successfully sent to {email}")
        return "success"
    
    except Exception as error:
        # Log any error that occurs
        logger.error(f"Failed to send reminder email to {email}: {str(error)}")
        raise ValueError("Falied to perform task")