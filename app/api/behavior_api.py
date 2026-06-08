from flask import Blueprint, jsonify, request

from app.core.response import error_response, success_response
from app.services.behavior_service import BehaviorService

behavior_bp = Blueprint('behavior_bp', __name__, url_prefix='/api/behavior')
service = BehaviorService()


@behavior_bp.post('/collect')
def collect_behavior():
    payload = request.get_json(silent=True) or {}
    result = service.collect_behavior(payload)
    if 'error' in result:
        return jsonify(error_response('BAD_REQUEST', result['error'], payload.get('request_id'), result['status_code'])), result['status_code']
    return jsonify(success_response(result, payload.get('request_id')))
