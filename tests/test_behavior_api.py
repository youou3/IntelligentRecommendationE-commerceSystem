def test_collect_behavior_success(client):
    payload = {
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ1',
        'event_id': 'EVT1',
        'user_id': 'U1',
        'event_type': 'product_click',
        'product_id': 'P1',
        'category_id': 'C1',
        'tags': ['running', 'summer'],
        'source': 'home_recommend',
        'duration': 15,
        'scene': 'home',
        'payload': {'device': 'ios'},
    }

    response = client.post('/api/behavior/collect', json=payload)
    assert response.status_code == 200
    body = response.get_json()
    assert body['success'] is True
    assert body['data']['accepted'] is True
    assert body['data']['duplicate'] is False
