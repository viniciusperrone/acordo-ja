from sqlalchemy import asc, desc
from .operators import OPERATORS


class BaseFilter:

    model = None
    fields = {}
    ordering_fields = []

    def __init__(self, query, params):
        self.query = query
        self.params = params

    def apply_filters(self):
        for param, value in self.params.items():

            if "__" in param:
                field_name, operator = param.split("__", 1)
            else:
                field_name = param
                operator = "exact"

            if field_name not in self.fields:
                continue

            if operator not in self.fields[field_name]:
                continue

            column = getattr(self.model, field_name, None)
            if not column:
                continue

            operation = OPERATORS.get(operator)
            if not operation:
                continue

            self.query = self.query.filter(operation(column, value))

        return self

    def apply_ordering(self):
        ordering_param = self.params.get("ordering")
        if not ordering_param:
            return self

        fields = ordering_param.split(",")

        for field in fields:
            direction = asc
            field_name = field

            if field.startswith("-"):
                direction = desc
                field_name = field[1:]

            if field_name in self.ordering_fields:
                column = getattr(self.model, field_name)
                self.query = self.query.order_by(direction(column))

        return self

    def apply(self):
        return (
            self
            .apply_filters()
            .apply_ordering()
            .query
        )