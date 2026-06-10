from flask import Blueprint, jsonify, request

from app.core.database import get_mongo_db
from app.core.mcp import skill_registry
from app.core.response import error_response, success_response
from app.core.validation import require_fields


mcp_bp = Blueprint('mcp_bp', __name__, url_prefix='/api/mcp')


@mcp_bp.get('/skills')
def list_skills():
    return jsonify(success_response({'items': skill_registry.list_skills()}, request.args.get('request_id')))


@mcp_bp.get('/skill-call-logs')
def skill_call_logs():
    payload = request.args
    missing = require_fields(payload, ['tenant_id', 'merchant_id', 'request_id'])
    if missing:
        return jsonify(error_response('BAD_REQUEST', f'missing fields: {", ".join(missing)}', payload.get('request_id'))), 400

    mongo_db = get_mongo_db()
    if mongo_db is None:
        return jsonify(success_response({'items': []}, payload.get('request_id')))

    limit = max(1, min(int(payload.get('limit', 50)), 200))
    query = {
        'tenant_id': payload['tenant_id'],
        'merchant_id': payload['merchant_id'],
    }
    if payload.get('skill_name'):
        query['skill_name'] = payload.get('skill_name')
    if payload.get('status'):
        query['status'] = payload.get('status')

    rows = list(mongo_db.skill_call_logs.find(query).sort('created_at', -1).limit(limit))
    items = []
    for row in rows:
        items.append({
            'skill_name': row.get('skill_name'),
            'skill_version': row.get('skill_version'),
            'request_id': row.get('request_id'),
            'status': row.get('status'),
            'cost_ms': row.get('cost_ms'),
            'error_message': row.get('error_message'),
            'fallback_used': row.get('fallback_used', False),
            'created_at': row.get('created_at').isoformat() if row.get('created_at') else None,
        })

    return jsonify(success_response({'items': items}, payload.get('request_id')))
