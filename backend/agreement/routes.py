from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from agreement import Agreement
from agreement.exceptions import DebtNotFountError, AgreementStatusError, PendingInstallmentsError, \
    AgreementNotFoundError
from agreement.schemas import AgreementSchema
from agreement.services import AgreementService
from installments import Installments

from config.db import db
from utils.enum import AgreementStatus

agreement_bp = Blueprint('agreement', __name__, url_prefix='/agreement')

@agreement_bp.route('/list', methods=['GET'])
def list_agreements():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pagination = Agreement.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        agreements_schema = AgreementSchema(many=True)

        result = agreements_schema.dump(pagination.items)

        return jsonify({
            "items": result,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page
        })

    except Exception as err:
        print(str(err))
        return jsonify({"message": "Internal Server Error"}), 500


@agreement_bp.route('/<uuid:agreement_id>/detail', methods=['GET'])
def get_agreement(agreement_id):
    try:
        agreement = AgreementService.get_agreement_or_fail(agreement_id)

        agreement_schema = AgreementSchema()
        result = agreement_schema.dump(agreement)

        return jsonify(result), 200
    except AgreementNotFoundError as err:
        return jsonify({'message': str(err)}), 400
    except Exception as err:
        return jsonify({"message": "Internal Server Error"}), 500

@agreement_bp.route('/add', methods=['POST'])
def create_agreement():
    agreement_schema = AgreementSchema()

    try:
        data = agreement_schema.load(request.json)

        AgreementService.create_agreement(data, db.session)

        return jsonify({"message": "Successfully registered agreement"}), 201

    except ValidationError as err:
        db.session.rollback()
        return jsonify({"message": err.messages}), 400
    except DebtNotFountError as err:
        db.session.rollback()
        return jsonify({'message': str(err)}), 400
    except Exception as err:
        print(str(err))

        db.session.rollback()
        return jsonify({"message": "Internal Server Error"}), 500

@agreement_bp.route('/<uuid:agreement_id>/cancel', methods=['POST'])
def cancel_agreement(agreement_id):
    try:
        agreement = AgreementService.get_agreement_or_fail(agreement_id)

        if not agreement:
            return jsonify({"message": "Agreement not found"}), 404

        AgreementService.cancel_agreement(agreement, db.session)

        return jsonify({"message": "Agreement successfully cancelled"}), 201

    except AgreementNotFoundError as err:
        return jsonify({'message': str(err)}), 400
    except AgreementStatusError as err:
        db.session.rollback()
        return jsonify({'message': str(err)}), 400
    except Exception as err:
        db.session.rollback()
        return jsonify({"message": "Internal Server Error"}), 500

@agreement_bp.route('/<uuid:agreement_id>/complete', methods=['POST'])
def complete_agreement(agreement_id):
    try:
        agreement = AgreementService.get_agreement_or_fail(agreement_id)

        AgreementService.complete_agreement(agreement, db.session)

        return jsonify({
            "message": "Agreement successfully completed"
        }), 200

    except AgreementNotFoundError as err:
        return jsonify({'message': str(err)}), 400

    except AgreementStatusError as err:
        db.session.rollback()
        return jsonify({'message': str(err)}), 400

    except PendingInstallmentsError as err:
        db.session.rollback()
        return jsonify({"message": str(err)}), 400

    except Exception as err:
        db.session.rollback()

        return jsonify({"message": "Internal Server Error"}), 500
