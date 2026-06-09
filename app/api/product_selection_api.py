from flask import Blueprint, jsonify, request

from app.core.response import error_response, success_response
from app.core.validation import require_fields
from app.services.product_selection_service import ProductSelectionService

product_selection_bp = Blueprint('product_selection_bp', __name__, url_prefix='/api/products')
service = ProductSelectionService()


@product_selection_bp.post('/selection-score')
def selection_score():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ['tenant_id', 'merchant_id', 'request_id'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400

    result = service.select_scores(
        tenant_id=payload['tenant_id'],
        merchant_id=payload['merchant_id'],
        request_id=payload['request_id'],
        product_ids=payload.get('product_ids'),
        date_range=payload.get('date_range'),
        persist=payload.get('persist', True),
    )
    return jsonify(success_response(result, payload.get('request_id')))
