from flask import Blueprint, request, jsonify

from config.db import db
from debts import Debt

debts_bp = Blueprint('debts', __name__, url_prefix='/debts')

@debts_bp.route('/add', methods=['POST'])
def create():
    data= request.json
    debt = Debt(**data)

    db.session.add(debt)
    db.session.commit()

    return jsonify({'message': 'Dívida cadastrada com sucesso'})