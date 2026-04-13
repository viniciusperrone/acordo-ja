from flask import Blueprint, request, jsonify, current_app, g
from marshmallow import ValidationError

from common.decorators.transactional import transactional
from .schemas import LeadSchema
from .services import LeadService


leads_bp = Blueprint('leads', __name__, url_prefix='/leads')

@leads_bp.route('/add', methods=['POST'])
@transactional
def create_lead(db):
    lead_schema = LeadSchema()

    try:
        data = lead_schema.load(request.json)
        document = request.args.get('document', None)

        lead = LeadService.create(data, document, session=db.session)

        current_app.logger.info(
            "Lead Created",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None),
            }
        )

        return jsonify(lead_schema.dump(lead)), 201

    except ValidationError as err:

        return jsonify({"errors": err.messages}), 400
    except Exception as err:
        current_app.logger.exception(
            "Error creating lead",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None),
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500
