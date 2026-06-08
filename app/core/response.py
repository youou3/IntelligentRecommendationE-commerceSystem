def success_response(data=None, request_id=None, message='success'):
    return {
        'success': True,
        'code': 'OK',
        'message': message,
        'request_id': request_id,
        'data': data or {},
    }


def error_response(code, message, request_id=None, status_code=400):
    return {
        'success': False,
        'code': code,
        'message': message,
        'request_id': request_id,
        'data': {'status_code': status_code},
    }
