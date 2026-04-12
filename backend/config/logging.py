import logging


class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.endpoint = getattr(record, "endpoint", None)
        record.method = getattr(record, "method", None)
        record.request_id = getattr(record, "request_id", None)
        record.params = getattr(record, "params", None)
        return super().format(record)