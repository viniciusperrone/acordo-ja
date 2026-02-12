from flask import Blueprint, request, jsonify

from config.db import db
from debtor.models import Debtor


debtor_bp = Blueprint('debtor', __name__, url_prefix='/debtor')

@debtor_bp.route('/add', methods=['POST'])
def create_debtor():
    data = request.get_json()
    debtor = Debtor(**data)
    db.session.add(debtor)

    return jsonify({"message": "Successfully registered debtor"})