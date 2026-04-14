from marshmallow import Schema, fields


class NotificationSchema(Schema):
    id = fields.UUID(dump_only=True)
    type = fields.Str(required=True)
    title = fields.Str(required=True)
    message = fields.Str(required=True)
    extra = fields.Dict(allow_none=True)
    user_id = fields.UUID(allow_none=True)
    is_read = fields.Bool(dump_only=True)
    read_at = fields.DateTime(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class NotificationFilterSchema(Schema):
    is_read = fields.Bool(allow_none=True)
    type = fields.Str(allow_none=True)
    user_id = fields.UUID(allow_none=True)


class MarkAsReadSchema(Schema):
    notification_ids = fields.List(fields.UUID(), required=True)
