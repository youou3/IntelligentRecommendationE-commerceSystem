from flask import Blueprint, jsonify, request

from app.core.response import error_response, success_response
from app.core.validation import require_fields
from app.services.recommendation_service import RecommendationService
from app.services.feedback_service import FeedbackService

recommendation_bp = Blueprint('recommendation_bp', __name__, url_prefix='/api/recommendations')
recommendation_service = RecommendationService()
feedback_service = FeedbackService()


@recommendation_bp.get('')
def recommendations():
    tenant_id = request.args.get('tenant_id')
    merchant_id = request.args.get('merchant_id')
    request_id = request.args.get('request_id')
    user_id = request.args.get('user_id')
    scene = request.args.get('scene', 'default')
    limit = int(request.args.get('limit', 10))

    missing = require_fields({
        'tenant_id': tenant_id,
        'merchant_id': merchant_id,
        'request_id': request_id,
        'user_id': user_id,
    }, ['tenant_id', 'merchant_id', 'request_id', 'user_id'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', request_id)), 400

    result = recommendation_service.recommend(tenant_id, merchant_id, user_id, scene, limit, request_id)
    if 'error' in result:
        return jsonify(error_response('SERVICE_UNAVAILABLE', result['error'], request_id, result['status_code'])), result['status_code']
    return jsonify(success_response(result, request_id))


@recommendation_bp.post('/feedback')
def recommendation_feedback():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ['tenant_id', 'merchant_id', 'request_id', 'event_id', 'user_id', 'product_id', 'feedback_type'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400

    result = feedback_service.log_feedback(payload)
    if 'error' in result:
        return jsonify(error_response('BAD_REQUEST', result['error'], payload.get('request_id'))), result['status_code']
    return jsonify(success_response(result, payload.get('request_id')))
