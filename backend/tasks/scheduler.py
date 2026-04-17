from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask

from .check_overdue import check_overdue_installments


def init_scheduler(app: Flask):

    scheduler = BackgroundScheduler(
        daemon=True,
        timezone='America/Sao_Paulo',
    )

    app.logger.info(
        "Initializing scheduler",
        extra={"timezone": "America/Sao_Paulo"}
    )

    scheduler.add_job(
        func=lambda: run_with_app_context(app, check_overdue_installments),
        trigger=CronTrigger(hour=9, minute=0),
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

    app.logger.info(
        "Scheduler started",
        extra={
            "jobs": [
                "check_overdue_installments",
                "cleanup_old_notification",
            ]
        }
    )

    scheduler.start()

def run_with_app_context(app: Flask, func):
    from flask import current_app
    from datetime import datetime

    with app.app_context():
        started_at = datetime.utcnow()

        current_app.logger.info(
            "Job started",
            extra={
                "job_name": func.__name__,
                "started_at": started_at.isoformat(),
            }
        )

        try:
            result = func()

            finished_at = datetime.utcnow()

            current_app.logger.info(
                "Job finished successfully",
                extra={
                    "job_name": func.__name__,
                    "started_at": started_at.isoformat(),
                    "finished_at": finished_at.isoformat(),
                }
            )

            return result

        except Exception as e:
            finished_at = datetime.utcnow()

            current_app.logger.exception(
                "Job failed",
                extra={
                    "job_name": func.__name__,
                    "started_at": started_at.isoformat(),
                    "finished_at": finished_at.isoformat(),
                    "error": str(e)
                }
            )

            raise

def cleanup_old_notification():
    from flask import current_app
    from datetime import datetime
    from notifications.services import NotificationService
    from config.db import db

    started_at = datetime.utcnow()

    try:
        current_app.logger.info(
            "Starting cleanup of old notification",
            extra={
                "days_threshold": 30,
                "started_at": started_at.isoformat(),
            }
        )

        count = NotificationService.delete_old_notifications(
            days=30,
            session=db.session
        )

        db.session.commit()

        current_app.logger.info(
            "Cleanup of odl notifications completed",
            extra={
                "deleted_count": count,
                "finished_at": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        db.session.rollback()

        current_app.logger.exception(
            "Error cleaning up old notifications",
            extra={
                "started_at": started_at.isoformat(),
                "error": str(e)
            }
        )

        raise
