from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from common.decorators import current_user
from config.transactional import transactional

from debts import Debt
from debts.schemas import DebtSchema, DebtSearchByDocumentSchema
from debts.services import DebtService
from debts.exceptions import DebtorNotExistError, CreditorNotExistError

debts_bp = Blueprint('debts', __name__, url_prefix='/debts')

@debts_bp.route('/list', methods=['GET'])
@jwt_required()
def list_debts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pagination = Debt.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        debts_schema = DebtSchema(many=True)

        result = debts_schema.dump(pagination.items)

        return jsonify({
            "items": result,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
        }), 200

    except Exception:
        current_app.logger.exception(
            "An error occured while listing debts",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({'message': 'Internal Server Error'}), 500

@debts_bp.route('/<uuid:debt_id>/detail', methods=['GET'])
@jwt_required()
@transactional
def retrieve_debt(debt_id, db):
    try:
        debt = db.session.get(Debt, debt_id)

        if not debt:
            return jsonify({'message': 'Debt not found'}), 404

        debt_schema = DebtSchema()
        result = debt_schema.dump(debt)

        return jsonify(result), 200
    except Exception:
        current_app.logger.exception(
            "An error occured while retrieving debt",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )
        return jsonify({'message': 'Internal Server Error'}), 500


@debts_bp.route('/add', methods=['POST'])
@jwt_required()
@transactional
@current_user
def create_debt(db):
    debt_schema = DebtSchema()

    try:
        data = debt_schema.load(request.json)

        DebtService.create_debt(
            data=data,
            session=db.session
        )

        user = g.current_user

        current_app.logger.info(
            'Created new debt',
            extra={
                "user_id": user.id,
                "user_role": getattr(user.role, 'value', None),
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),

                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({'message': 'Successfully registered debt'}), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except DebtorNotExistError as err:
        current_app.logger.warning(
            'Debtor not found while creating new debt',
            extra={
                "user_id": current_user.id,
                "error": str(err),
                "endpoint": request.path,
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({'message': str(err)}), 400
    except CreditorNotExistError as err:
        current_app.logger.warning(
            'Creditor not found while creating debt',
            extra={
                "user_id": current_user.id,
                "error": str(err),
                "endpoint": request.path,
                "request_id": getattr(g, "request_id", None)
            }
        )
        return jsonify({'message': str(err)}), 400
    except Exception as err:
        print(str(err))

        current_app.logger.exception(
            "An error occured while creating debt",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500


@debts_bp.route('/search', methods=['GET'])
@jwt_required()
def search_debt():
    debt_schema = DebtSearchByDocumentSchema()
    debts_schema = DebtSchema(many=True)

    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        data = debt_schema.load(request.args)

        query = (
            Debt.query
            .join(Debt.debtor)
            .filter(Debt.debtor.has(document=data['document']))
        )

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        result = debts_schema.dump(pagination.items)

        return jsonify({
            "items": result,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
        }), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    except Exception:
        current_app.logger.exception(
            "An error occured while searching debt",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500
