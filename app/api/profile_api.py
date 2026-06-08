from flask import Blueprint, jsonify, request

from app.core.response import error_response, success_response
from app.core.validation import require_fields
from app.services.profile_service import ProfileService

profile_bp = Blueprint('profile_bp', __name__, url_prefix='/api/user-profiles')
service = ProfileService()


@profile_bp.post('/generate')
def generate_profile():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ['tenant_id', 'merchant_id', 'request_id', 'user_id'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400

    result = service.generate_profile(payload['tenant_id'], payload['merchant_id'], payload['user_id'])
    if 'error' in result:
        return jsonify(error_response('SERVICE_UNAVAILABLE', result['error'], payload.get('request_id'), result['status_code'])), result['status_code']
    return jsonify(success_response(result, payload.get('request_id')))
