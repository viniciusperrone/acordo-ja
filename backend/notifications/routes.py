from flask import Blueprint, request, g, jsonify, current_app
from flask_jwt_extended import jwt_required

from common.decorators import current_user, transactional
from notifications.models import Notification
from notifications.schemas import NotificationSchema
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
            "An error occured while fetching notifications",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )
        return jsonify({"message": "Internal Server Error"}), 500
