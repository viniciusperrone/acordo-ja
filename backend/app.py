from flask import Flask
from flask_migrate import Migrate

from config.db import db
from config.config import Config

import debts

from debts.routes import debts_bp


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)

app.register_blueprint(debts_bp)

migrate = Migrate(app, db)

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
    )

