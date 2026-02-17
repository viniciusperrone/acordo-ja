from sqlalchemy import event
from sqlalchemy.orm import Session

from creditor import Creditor


@event.listens_for(Creditor, "before_delete")
def prevent_delete(mapper, connection, target):
    raise ValueError("Creditor can't be deleted")

@event.listens_for(Creditor, "before_update")
def prevent_update(mapper, connection, target):
    raise ValueError("Creditor can't be updated")
