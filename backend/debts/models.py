from config.db import db


class Debt(db.Model):
    __tablename__ = 'debts'

    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), nullable=False)
    creditor = db.Column(db.String(100))
    original_value = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date)