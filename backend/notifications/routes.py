from flask import Blueprint, request, g, jsonify, current_app
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from common.decorators import current_user, transactional
from notifications import Notification
from notifications.models import Notification
from notifications.schemas import NotificationSchema, MarkAsReadSchema
from notifications.services import NotificationService
from notifications.filters import NotificationFilter


notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/list', methods=['GET'])
@jwt_required()
@transactional
@current_user
def list_notifications(db):
    try:
        current_user_id = g.current_user.id

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        query = Notification.query.filter(
            Notification.user_id == current_user_id,
        )

        query = NotificationFilter(query, request.args).apply()

        query = query.order_by(Notification.created_at.desc())

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        notification_schema = NotificationSchema(many=True)

        result = notification_schema.dump(pagination.items)

        return jsonify({
            "items": result,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "unread_count": NotificationService.get_unread_count(current_user_id)
        })

    except Exception as err:
        current_app.logger.exception(
            "An error occurred while fetching notifications",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )
        return jsonify({"message": "Internal Server Error"}), 500

@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
@transactional
@current_user
def get_unread_count():
    try:
        current_user_id = g.current_user.id
        count = NotificationService.get_unread_count(current_user_id)

        return jsonify({"unread_count": count}), 200
    except Exception as err:
        current_app.logger.exception(
            "An error occurred while fetch notification",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500

@notifications_bp.route('/<uuid:notification_id>/mark-read', methods=['PATCH'])
@jwt_required()
@transactional
@current_user
def mark_notification_as_read(notification_id, db):
    try:
        current_user_id = g.current_user.id

        notification = db.session.get(Notification, notification_id)

        if not notification:
            return jsonify({"message": "Notification not found"}), 404

        if str(notification.user_id) != str(current_user_id):
            return jsonify({"message": "Unauthorized access"}), 401

        NotificationService.mark_as_read(notification_id, session=db.session)

        return jsonify({"message": "Notification marked as read"}), 200

    except Exception as err:
        current_app.logger.exception(
            "An error occurred while marking notification as read",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500

@notifications_bp.route('/mark-read-bulk', methods=['PATCH'])
@jwt_required()
@transactional
@current_user
def mark_multiple_as_read(db):
    mark_schema = MarkAsReadSchema()

    try:
        current_user_id = g.current_user.id
        data = mark_schema.load(request.json)

        notifications = Notification.query.filter(
            Notification.id.in_(data['notification_ids'])
        ).all()

        for notification in notifications:
            if str(notification.user_id) != current_user_id:
                return jsonify({"message": "Unauthorized access"}), 401

        count = NotificationService.mark_multiple_as_read(
            data['notification_ids'],
            session=db.session
        )

        return jsonify({
            "message": f"{count} notifications marked as read",
        }), 200

    except ValidationError as err:
        return jsonify({"message": err.messages}), 400
    except Exception as err:
        current_app.logger.exception(
            "An error occurred while marking notifications as read",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500

@notifications_bp.route('/mark-all-read', methods=['PATCH'])
@jwt_required()
@transactional
@current_user
def mark_all_as_read(db):
    try:
        current_user_id = g.current_user.id

        count = NotificationService.mark_all_read_for_user(
            current_user_id,
            session=db.session
        )

        return jsonify({"message": f"{count} notifications marked as read"}), 200
    except Exception as err:
        current_app.logger.exception(
            "An error occurred while marking notifications as read",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500