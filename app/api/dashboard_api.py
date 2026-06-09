from flask import Blueprint, jsonify, request

from app.core.response import error_response, success_response
from app.core.validation import require_fields
from app.services.dashboard_service import DashboardService


dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/api/dashboard')
service = DashboardService()


@dashboard_bp.get('/overview')
def overview():
    payload = request.args.to_dict(flat=True)
    missing = require_fields(payload, ['tenant_id', 'merchant_id'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400
    try:
        filters = service._parse_filters(payload)
    except ValueError as exc:
        return jsonify(error_response('BAD_REQUEST', str(exc), payload.get('request_id'))), 400
    return jsonify(success_response(service.get_overview(filters), payload.get('request_id')))


@dashboard_bp.get('/recommendation-funnel')
def recommendation_funnel():
    payload = request.args.to_dict(flat=True)
    missing = require_fields(payload, ['tenant_id', 'merchant_id'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400
    try:
        filters = service._parse_filters(payload)
    except ValueError as exc:
        return jsonify(error_response('BAD_REQUEST', str(exc), payload.get('request_id'))), 400
    return jsonify(success_response(service.get_recommendation_funnel(filters), payload.get('request_id')))


@dashboard_bp.get('/product-selection')
def product_selection():
    payload = request.args.to_dict(flat=True)
    missing = require_fields(payload, ['tenant_id', 'merchant_id'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400
    try:
        filters = service._parse_filters(payload)
    except ValueError as exc:
        return jsonify(error_response('BAD_REQUEST', str(exc), payload.get('request_id'))), 400
    return jsonify(success_response(service.get_product_selection(filters), payload.get('request_id')))


@dashboard_bp.get('/user-profiles')
def user_profiles():
    payload = request.args.to_dict(flat=True)
    missing = require_fields(payload, ['tenant_id', 'merchant_id'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400
    try:
        filters = service._parse_filters(payload)
    except ValueError as exc:
        return jsonify(error_response('BAD_REQUEST', str(exc), payload.get('request_id'))), 400
    return jsonify(success_response(service.get_user_profiles(filters), payload.get('request_id')))


@dashboard_bp.get('/inventory-health')
def inventory_health():
    payload = request.args.to_dict(flat=True)
    missing = require_fields(payload, ['tenant_id', 'merchant_id'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400
    try:
        filters = service._parse_filters(payload)
    except ValueError as exc:
        return jsonify(error_response('BAD_REQUEST', str(exc), payload.get('request_id'))), 400
    return jsonify(success_response(service.get_inventory_health(filters), payload.get('request_id')))
