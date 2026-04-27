from flask import Blueprint, request, jsonify

from common.decorators import transactional
from config.rate_limit import limiter

from leads.schemas import LeadSchema
from leads.services import LeadService


leads_bp = Blueprint('leads', __name__, url_prefix='/leads')

@leads_bp.route('/add', methods=['POST'])
@limiter.limit('5 per minute')
@transactional
def create_lead(db):
    document = request.args.get('document', None)

    lead_schema = LeadSchema()
    data = lead_schema.load(request.json)

    lead = LeadService.create(data, document, session=db.session)

    return jsonify(lead_schema.dump(lead)), 201
