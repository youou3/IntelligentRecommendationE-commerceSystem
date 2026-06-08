def require_fields(payload, fields):
    missing = [field for field in fields if payload.get(field) in (None, '')]
    return missing


def get_request_context(payload_or_args):
    return {
        'tenant_id': payload_or_args.get('tenant_id'),
        'merchant_id': payload_or_args.get('merchant_id'),
        'request_id': payload_or_args.get('request_id'),
        'scene': payload_or_args.get('scene'),
        'event_id': payload_or_args.get('event_id'),
    }
