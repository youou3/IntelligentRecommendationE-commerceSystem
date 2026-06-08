from app.core.database import db
from app.models.recommendation_feedback import RecommendationFeedback


def test_feedback_api_click(client, app):
    response = client.post('/api/recommendations/feedback', json={
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ4',
        'event_id': 'FB1',
        'user_id': 'U1',
        'product_id': 'P1',
        'scene': 'home',
        'feedback_type': 'click',
    })
    assert response.status_code == 200
    body = response.get_json()
    assert body['success'] is True
    assert body['data']['accepted'] is True

    with app.app_context():
        row = RecommendationFeedback.query.filter_by(tenant_id='T1', merchant_id='M1', event_id='FB1').first()
        assert row is not None
        assert row.click_flag is True


def test_feedback_api_add_cart(client, app):
    response = client.post('/api/recommendations/feedback', json={
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ5',
        'event_id': 'FB2',
        'user_id': 'U1',
        'product_id': 'P1',
        'scene': 'home',
        'feedback_type': 'add_cart',
    })
    assert response.status_code == 200
    body = response.get_json()
    assert body['data']['accepted'] is True


def test_feedback_api_invalid_type(client):
    response = client.post('/api/recommendations/feedback', json={
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ6',
        'event_id': 'FB3',
        'user_id': 'U1',
        'product_id': 'P1',
        'scene': 'home',
        'feedback_type': 'unknown',
    })
    assert response.status_code == 400
