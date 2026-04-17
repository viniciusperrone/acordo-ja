from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask

from .check_overdue import check_overdue_installments


def init_scheduler(app: Flask):

    scheduler = BackgroundScheduler(
        daemon=True,
        timezone='America/Sao_Paulo',
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

    scheduler.start()


def run_with_app_context(app: Flask, func):

    with app.app_context():
        return func()

def cleanup_old_notification():
    from notifications.services import NotificationService
    from config.db import db

    try:
        count = NotificationService.delete_old_notifications(days=30, session=db.session)

        db.session.commit()

    except Exception as e:
        db.session.rollback()

        raise

