from sqlalchemy import or_

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

    enum_type = getattr(column.type, "python__type", None)

    if enum_type:
        try:
            values = [enum_type(v) for v in values]
        except Exception:
            pass

    return column.in_(value.split(","))

OPERATORS = {
    "exact": op_exact,
    "gte": op_gte,
    "lte": op_lte,
    "like": op_like,
    "in": op_in,
}
