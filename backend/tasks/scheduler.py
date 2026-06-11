from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, current_app

from config.db import db
from notifications.services import NotificationService
from observability.structured_logger import log_event, get_logger
from observability.tracing import traced
from .check_overdue import check_overdue_installments


logger = get_logger("tasks.scheduler")


@traced("tasks.scheduler.init_scheduler")
def init_scheduler(app: Flask):

    scheduler = BackgroundScheduler(
        daemon=True,
        timezone='America/Sao_Paulo',
    )

    log_event(
        logger,
        "info",
        "tasks.scheduler.init_scheduler",
        extra_fields={
            "message": "Initializing scheduler",
            "timezone": "America/Sao_Paulo"
        }
    )

    scheduler.add_job(
        func=lambda: run_with_app_context(app, check_overdue_installments),
        trigger=CronTrigger(hour=15, minute=3),
        id='check_overdue_installments',
        name='Check overdue payments',
        replace_existing=True,
        misfire_grace_time=3600,
    )

    scheduler.add_job(
        func=lambda: run_with_app_context(app, cleanup_old_notification),
        trigger=CronTrigger(hour=3, minute=0),
        id='cleanup_old_notification',
        name='Cleanup old notifications',
        replace_existing=True,
        misfire_grace_time=3600,
    )

    log_event(
        logger,
        "info",
        "tasks.scheduler.scheduler_started",
        extra_fields={
            "message": "Scheduler started",
            "jobs": [
                "check_overdue_installments",
                "cleanup_old_notification",
            ]
        }
    )

    scheduler.start()


def run_with_app_context(app: Flask, func):
    from datetime import datetime

    with app.app_context():
        started_at = datetime.utcnow()

        log_event(
            logger,
            "info",
            "tasks.scheduler.job_started",
            extra_fields={
                "message": "Job started",
                "job_name": func.__name__,
                "started_at": started_at.isoformat(),
            }
        )

        try:
            result = func()

            finished_at = datetime.utcnow()

            log_event(
                logger,
                "info",
                "tasks.scheduler.job_completed",
                extra_fields={
                    "message": "Job finished successfully",
                    "job_name": func.__name__,
                    "started_at": started_at.isoformat(),
                    "finished_at": finished_at.isoformat(),
                }
            )

            return result

        except Exception as e:
            finished_at = datetime.utcnow()

            log_event(
                logger,
                "error",
                "tasks.scheduler.job_failed",
                extra_fields={
                    "message": "Job failed",
                    "job_name": func.__name__,
                    "started_at": started_at.isoformat(),
                    "finished_at": finished_at.isoformat(),
                    "error": str(e)
                }
            )

            raise


def cleanup_old_notification():
    started_at = datetime.utcnow()

    try:
        log_event(
            logger,
            "info",
            "tasks.scheduler.clean_old_notifications",
            extra_fields={
                "message": "Starting cleanup of old notifications",
                "days_threshold": 30,
                "started_at": started_at.isoformat(),
            }
        )

        count = NotificationService.delete_old_notifications(
            days=30,
            session=db.session
        )

        db.session.commit()

        log_event(
            logger,
            "info",
            "tasks.scheduler.cleanup_old_notifications_finished",
            extra_fields={
                "message": "Cleanup of old notifications completed",
                "deleted_count": count,
                "finished_at": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        db.session.rollback()

        log_event(
            current_app.logger,
            "error",
            "tasks.scheduler.cleanup_old_notifications_failed",
            extra_fields={
                "message": "Error cleaning up old notifications",
                "started_at": started_at.isoformat(),
                "error": str(e)
            }
        )

        raise
