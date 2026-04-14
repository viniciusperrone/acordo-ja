import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from config.db import db
from config.config import Config
from config.logging import CustomFormatter

import creditor
import debts
import debtor
import agreement
import installments
import payment
import users
import notifications
import leads

from creditor.routes import creditor_bp
from debts.routes import debts_bp
from debtor.routes import debtor_bp
from installments.routes import installment_bp
from agreement.routes import agreement_bp
from payment.routes import payment_bp
from leads.routes import leads_bp
from users.routes import user_bp
from authentication.routes import authentication_bp
from notifications.routes import notifications_bp


def setup_logging(app):
    if not os.path.exists("logs"):
        os.mkdir("logs")

    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10240,
        backupCount=10
    )

    formatter = CustomFormatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s | "
        "endpoint=%(endpoint)s method=%(method)s request_id=%(request_id)s"
    )

    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    app.logger.info("Logging configurado com sucesso")


def initialize_app():
    app = Flask(__name__)

    if os.getenv("TESTING") == "True":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
        app.config["TESTING"] = True
    else:
        app.config.from_object(Config)

    db.init_app(app)
    jwt = JWTManager(app)

    setup_logging(app)

    app.register_blueprint(creditor_bp)
    app.register_blueprint(debts_bp)
    app.register_blueprint(debtor_bp)
    app.register_blueprint(installment_bp)
    app.register_blueprint(agreement_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(authentication_bp)
    app.register_blueprint(notifications_bp)

    Migrate(app, db)

    return app


if __name__ == '__main__':
    app = initialize_app()

    app.run(
        host='0.0.0.0',
        port=5000,
    )