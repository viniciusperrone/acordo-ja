from sqlalchemy import or_
import uuid


def op_exact(column, value):
    return column == value

def op_gte(column, value):
    return column >= value

def op_lte(column, value):
    return column <= value

def op_like(column, value):
    return column.ilike(f"%{value}%")

def op_in(column, value):
    values = value.split(",")

    python_type = getattr(column.type, "python_type", None)

    if python_type:
        try:
            if python_type is uuid.UUID:
                values = [uuid.UUID(v) for v in values]
            else:
                values = [python_type(v) for v in values]
        except Exception:
            pass

    return column.in_(values)

OPERATORS = {
    "exact": op_exact,
    "gte": op_gte,
    "lte": op_lte,
    "like": op_like,
    "in": op_in,
}
