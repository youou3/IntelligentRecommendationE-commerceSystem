from app.core.database import db
from app.models.product import Product
from app.models.user_profile import UserProfile


def test_generate_profile(client, app):
    with app.app_context():
        from app.core.database import get_mongo_db
        mongo_db = get_mongo_db()
        mongo_db.behavior_events.insert_many([ # type: ignore
            {
                'tenant_id': 'T1',
                'merchant_id': 'M1',
                'event_id': 'EVT1',
                'request_id': 'REQ1',
                'event_type': 'product_click',
                'scene': 'home',
                'user_id': 'U1',
                'product_id': 'P1',
                'category_id': 'C1',
                'tags': ['running', 'summer'],
                'source': 'home_recommend',
                'payload': {},
                'created_at': __import__('datetime').datetime.utcnow(),
            },
            {
                'tenant_id': 'T1',
                'merchant_id': 'M1',
                'event_id': 'EVT2',
                'request_id': 'REQ2',
                'event_type': 'add_cart',
                'scene': 'home',
                'user_id': 'U1',
                'product_id': 'P2',
                'category_id': 'C1',
                'tags': ['running'],
                'source': 'home_recommend',
                'payload': {},
                'created_at': __import__('datetime').datetime.utcnow(),
            },
        ])

    response = client.post('/api/user-profiles/generate', json={
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ3',
        'user_id': 'U1',
    })
    assert response.status_code == 200
    body = response.get_json()
    assert body['success'] is True
    assert body['data']['user_stage'] == 'strong_intent'
    assert body['data']['tag_vector']['running'] > 0

    with app.app_context():
        profile = UserProfile.query.filter_by(tenant_id='T1', merchant_id='M1', user_id='U1').first()
        assert profile is not None


def test_recommendation_api(client, app):
    with app.app_context():
        db.session.add(Product(
            id='P1', tenant_id='T1', merchant_id='M1', name='Running Shoes', category_id='C1',
            tags=['running', 'summer'], price=99, cost_price=50, gross_margin=0.49, status='active'
        ))
        db.session.add(Product(
            id='P2', tenant_id='T1', merchant_id='M1', name='Jacket', category_id='C2',
            tags=['winter'], price=129, cost_price=70, gross_margin=0.46, status='active'
        ))
        db.session.add(UserProfile(
            tenant_id='T1', merchant_id='M1', user_id='U1', tag_vector={'running': 3, 'summer': 1},
            category_preference={'C1': 2}, price_preference={}, user_stage='active_browsing'
        ))
        db.session.commit()

    response = client.get('/api/recommendations', query_string={
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ4',
        'user_id': 'U1',
        'scene': 'home',
        'limit': 10,
    })
    assert response.status_code == 200
    body = response.get_json()
    assert body['success'] is True
    assert len(body['data']['items']) >= 1
    assert body['data']['items'][0]['product_id'] == 'P1'
