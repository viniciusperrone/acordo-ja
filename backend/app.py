import os

from flask import Flask
from flask_migrate import Migrate

from common.handlers.error_handlers import register_error_handlers
from observability.middleware import Observability
from observability.tracing import setup_tracing
from observability.metrics import Metrics

from config import (
    Config,
    db,
    limiter,
    rate_limit_handler,
    init_jwt,
)

import creditor
import debts
import debtor
import agreement
import installments
import payment
import users
import notifications
import leads
import authentication

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


def initialize_app():
    app = Flask(__name__)

    if os.getenv("TESTING") == "True":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
        app.config["TESTING"] = True
    else:
        app.config.from_object(Config)

    db.init_app(app)
    init_jwt(app)

    limiter.init_app(app)

    app.register_error_handler(429, rate_limit_handler)

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

    register_error_handlers(app)

    Migrate(app, db)

    Observability(app)
    Metrics.setup(app)

    if not app.config.get("TESTING"):
        setup_tracing(app)
        from tasks.scheduler import init_scheduler
        init_scheduler(app)

    return app


if __name__ == '__main__':
    app = initialize_app()

    app.run(
        host='0.0.0.0',
        port=5000,
    )
