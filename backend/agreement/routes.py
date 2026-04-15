from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from agreement import Agreement
from agreement.exceptions import (
    DebtNotFountError,
    AgreementStatusError,
    PendingInstallmentsError,
    AgreementNotFoundError
)
from agreement.schemas import AgreementSchema
from agreement.services import AgreementService

from common.decorators import transactional, current_user


agreement_bp = Blueprint('agreement', __name__, url_prefix='/agreement')

@agreement_bp.route('/list', methods=['GET'])
@jwt_required()
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

    except Exception:
        current_app.logger.exception(
            "An error occured while retrieving agreements",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None),
            }
        )
        return jsonify({"message": "Internal Server Error"}), 500


@agreement_bp.route('/<uuid:agreement_id>/detail', methods=['GET'])
@jwt_required()
def get_agreement(agreement_id):
    try:
        agreement = AgreementService.get_agreement_or_fail(agreement_id)

        agreement_schema = AgreementSchema()
        result = agreement_schema.dump(agreement)

        return jsonify(result), 200

    except AgreementNotFoundError as err:
        return jsonify({'message': str(err)}), 400

    except Exception:
        current_app.logger.exception(
            "An error occured while retrieving agreement",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None),
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500

@agreement_bp.route('/add', methods=['POST'])
@jwt_required()
@transactional
@current_user
def create_agreement(db):
    agreement_schema = AgreementSchema()

    try:
        data = agreement_schema.load(request.json)

        AgreementService.create_agreement(data, db.session)

        user = g.current_user

        current_app.logger.info(
            "Agreement created successfully",
            extra={
                "user_id": user.id,
                "user_role": getattr(user.role, "value", None),
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None),
            }
        )

        return jsonify({"message": "Successfully registered agreement"}), 201

    except ValidationError as err:
        return jsonify({"message": err.messages}), 400
    except DebtNotFountError as err:
        return jsonify({'message': str(err)}), 400
    except Exception as err:
        current_app.logger.exception(
            "An error occured while creating agreement",
            extra={
                "user_id": user.id,
                "user_role": getattr(user.role, "value", None),
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None),
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500

@agreement_bp.route('/<uuid:agreement_id>/activate', methods=['PATCH'])
@jwt_required()
@transactional
def activate_agreement(agreement_id, db):
    try:
        agreement = AgreementService.get_agreement_or_fail(agreement_id)

        agreement = AgreementService.open_agreement(agreement, db.session)

        return jsonify({"message": "Agreement has been opened"}), 200
    except AgreementNotFoundError as err:
        return jsonify({'message': str(err)}), 404
    except AgreementStatusError as err:
        return jsonify({'message': str(err)}), 400
    except Exception as err:
        current_app.logger.exception(
            "An error occurred while opening agreement",
            extra={
                "agreement_id": agreement_id,
                "endpoint": request.endpoint,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None),
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500


@agreement_bp.route('/<uuid:agreement_id>/cancel', methods=['POST'])
@transactional
def cancel_agreement(agreement_id, db):
    try:
        agreement = AgreementService.get_agreement_or_fail(agreement_id)

        AgreementService.cancel_agreement(agreement, db.session)

        current_app.logger.info(
            "Agreement canceled successfully",
            extra={
                "agreement_id": agreement_id,
                "debt_id": getattr(agreement, "debt_id", None),
                "endpoint": request.endpoint,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None),
            }
        )

        return jsonify({"message": "Agreement successfully cancelled"}), 201

    except AgreementNotFoundError as err:
        return jsonify({'message': str(err)}), 404
    except AgreementStatusError as err:
        return jsonify({'message': str(err)}), 400
    except Exception:
        current_app.logger.exception(
            "An error occured while cancelling agreement",
            extra={
                "agreement_id": agreement_id,
                "endpoint": request.endpoint,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None),
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500

@agreement_bp.route('/<uuid:agreement_id>/complete', methods=['POST'])
@transactional
def complete_agreement(agreement_id, db):
    try:
        agreement = AgreementService.get_agreement_or_fail(agreement_id)

        AgreementService.complete_agreement(agreement, db.session)

        current_app.logger.info(
            "Agreement completed successfully",
            extra={
                "agreement_id": agreement_id,
                "debt_id": getattr(agreement, "debt_id", None),
                "endpoint": request.endpoint,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None),
            }
        )

        return jsonify({
            "message": "Agreement successfully completed"
        }), 200

    except AgreementNotFoundError as err:
        return jsonify({'message': str(err)}), 404

    except AgreementStatusError as err:
        return jsonify({'message': str(err)}), 400

    except PendingInstallmentsError as err:
        return jsonify({"message": str(err)}), 400

    except Exception:
        current_app.logger.exception(
            "An error occured while cancelling agreement",
            extra={
                "agreement_id": agreement_id,
                "debt_id": getattr(agreement, "debt_id", None),
                "endpoint": request.endpoint,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None),
            }
        )
        return jsonify({"message": "Internal Server Error"}), 500
