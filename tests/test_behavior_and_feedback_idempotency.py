from app.core.database import get_mongo_db
from app.models.recommendation_feedback import RecommendationFeedback


def test_collect_behavior_idempotent(client, app):
    payload = {
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ1',
        'event_id': 'EVT1',
        'user_id': 'U1',
        'event_type': 'product_click',
        'product_id': 'P1',
        'category_id': 'C1',
        'tags': ['running'],
        'source': 'home_recommend',
        'duration': 15,
        'scene': 'home',
        'payload': {},
    }

    first = client.post('/api/behavior/collect', json=payload)
    second = client.post('/api/behavior/collect', json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.get_json()['data']['duplicate'] is True

    with app.app_context():
        mongo_db = get_mongo_db()
        assert mongo_db.behavior_events.count_documents({'tenant_id': 'T1', 'merchant_id': 'M1', 'event_id': 'EVT1'}) == 1


def test_feedback_idempotent(client, app):
    payload = {
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ2',
        'event_id': 'FB1',
        'user_id': 'U1',
        'product_id': 'P1',
        'scene': 'home',
        'feedback_type': 'click',
    }

    first = client.post('/api/recommendations/feedback', json=payload)
    second = client.post('/api/recommendations/feedback', json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.get_json()['data']['duplicate'] is True

    with app.app_context():
        assert RecommendationFeedback.query.filter_by(tenant_id='T1', merchant_id='M1', event_id='FB1').count() == 1
