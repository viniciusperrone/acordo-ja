import os

from flask import Flask
from flask_migrate import Migrate

from config.db import db
from config.config import Config

import creditor
import debts
import debtor
import agreement
import installments

from creditor.routes import creditor_bp
from debts.routes import debts_bp
from debtor.routes import debtor_bp
from installments.routes import installment_bp
from agreement.routes import agreement_bp


def initialize_app():
    app = Flask(__name__)

    if os.getenv("TESTING") == "True":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
        app.config["TESTING"] = True
    else:
        app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(creditor_bp)
    app.register_blueprint(debts_bp)
    app.register_blueprint(debtor_bp)
    app.register_blueprint(installment_bp)
    app.register_blueprint(agreement_bp)

    Migrate(app, db)

    return app


if __name__ == '__main__':
    app = initialize_app()

    app.run(
        host='0.0.0.0',
        port=5000,
    )