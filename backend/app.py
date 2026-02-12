import os

from flask import Flask
from flask_migrate import Migrate

from config.db import db
from config.config import Config

import debts
import debtor
import agreement

from debts.routes import debts_bp
from debtor.routes import debtor_bp


def initialize_app():
    app = Flask(__name__)

    if os.getenv("TESTING") == "True":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
        app.config["TESTING"] = True
    else:
        app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(debts_bp)
    app.register_blueprint(debtor_bp)

    Migrate(app, db)

    return app


if __name__ == '__main__':
    app = initialize_app()

    app.run(
        host='0.0.0.0',
        port=5000,
    )