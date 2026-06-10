from flask import Blueprint, jsonify, request

from app.core.response import error_response, success_response
from app.core.validation import require_fields
from app.services.inventory_service import InventoryService


inventory_bp = Blueprint('inventory_bp', __name__, url_prefix='/api/inventory')
service = InventoryService()


@inventory_bp.get('/warnings')
def warnings():
    payload = request.args
    missing = require_fields(payload, ['tenant_id', 'merchant_id', 'request_id'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400

    page = max(1, int(payload.get('page', 1)))
    page_size = max(1, min(int(payload.get('page_size', 20)), 100))
    result = service.list_warnings(
        tenant_id=payload['tenant_id'],
        merchant_id=payload['merchant_id'],
        request_id=payload.get('request_id'),
        warning_level=payload.get('warning_level'),
        category_id=payload.get('category_id'),
        status=payload.get('status'),
        page=page,
        page_size=page_size,
    )
    return jsonify(success_response(result, payload.get('request_id')))


@inventory_bp.post('/warnings/run')
def run_warnings():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ['tenant_id', 'merchant_id', 'request_id'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400

    result = service.run_warning_workflow(
        tenant_id=payload['tenant_id'],
        merchant_id=payload['merchant_id'],
        request_id=payload['request_id'],
        product_ids=payload.get('product_ids'),
        sales_days=int(payload.get('sales_days', 7)),
        persist=payload.get('persist', True),
    )
    return jsonify(success_response(result, payload.get('request_id')))


@inventory_bp.post('/replenishment/suggest')
def suggest_replenishment():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ['tenant_id', 'merchant_id', 'request_id', 'product_id'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400

    try:
        result = service.suggest_replenishment(
            tenant_id=payload['tenant_id'],
            merchant_id=payload['merchant_id'],
            request_id=payload['request_id'],
            product_id=payload['product_id'],
            forecast_days=int(payload.get('forecast_days', 14)),
            warning_id=payload.get('warning_id'),
            persist=payload.get('persist', True),
        )
    except ValueError as exc:
        return jsonify(error_response('NOT_FOUND', str(exc), payload.get('request_id'), 404)), 404
    return jsonify(success_response(result, payload.get('request_id')))


@inventory_bp.post('/events')
def inventory_event():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ['tenant_id', 'merchant_id', 'request_id', 'event_id', 'product_id', 'change_type', 'quantity'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400

    try:
        result = service.apply_inventory_event(
            tenant_id=payload['tenant_id'],
            merchant_id=payload['merchant_id'],
            request_id=payload['request_id'],
            event_id=payload['event_id'],
            product_id=payload['product_id'],
            change_type=payload['change_type'],
            quantity=payload['quantity'],
        )
    except ValueError as exc:
        return jsonify(error_response('BAD_REQUEST', str(exc), payload.get('request_id'))), 400
    return jsonify(success_response(result, payload.get('request_id')))
