# from sqlalchemy import event
#
# from config.db import db
# from debts.models import Debt, DebtHistory
#
#
# @event.listens_for(Debt, "before_update")
# def track_debt_changes(mapper, connection, target):
#     state = db.inspect(target)
#
#     if state.attrs