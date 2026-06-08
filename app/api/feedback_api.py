from flask import Blueprint, jsonify, request

from app.core.response import error_response, success_response
from app.core.validation import require_fields
from app.services.feedback_service import FeedbackService

feedback_bp = Blueprint('feedback_bp', __name__, url_prefix='/api/feedback')
service = FeedbackService()


@feedback_bp.post('')
def log_feedback():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ['tenant_id', 'merchant_id', 'request_id', 'event_id', 'user_id', 'product_id', 'feedback_type'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400

    result = service.log_feedback(payload)
    if 'error' in result:
        return jsonify(error_response('BAD_REQUEST', result['error'], payload.get('request_id'))), result['status_code']
    return jsonify(success_response(result, payload.get('request_id')))
