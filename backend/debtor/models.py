from datetime import datetime as dt
from config.db import db


class Debtor(db.Model):
    __tablename__ = 'debtors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    document = db.Column(db.String(14), nullable=False, unique=True)
    email = db.Column(db.String(150))
    phone = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=dt.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=dt.utcnow)
