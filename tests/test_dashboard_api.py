from datetime import datetime, timedelta

from app.core.database import db, get_mongo_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.recommendation_feedback import RecommendationFeedback
from app.models.user_profile import UserProfile


def _seed_dashboard_data(app):
    with app.app_context():
        mongo_db = get_mongo_db()
        now = datetime.utcnow()
        mongo_db.behavior_events.insert_many([
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
                'tags': ['running'],
                'source': 'home',
                'payload': {},
                'created_at': now,
            },
            {
                'tenant_id': 'T1',
                'merchant_id': 'M1',
                'event_id': 'EVT2',
                'request_id': 'REQ2',
                'event_type': 'product_view',
                'scene': 'home',
                'user_id': 'U2',
                'product_id': 'P2',
                'category_id': 'C2',
                'tags': ['summer'],
                'source': 'home',
                'payload': {},
                'created_at': now - timedelta(days=1),
            },
        ])
        mongo_db.recommendation_logs.insert_one({
            'tenant_id': 'T1',
            'merchant_id': 'M1',
            'request_id': 'REQ_REC',
            'user_id': 'U1',
            'scene': 'home',
            'recommended_products': ['P1'],
            'clicked_products': ['P1'],
            'converted_products': [],
            'created_at': now,
        })
        db.session.add_all([
            Product(id='P1', tenant_id='T1', merchant_id='M1', name='Running Shoes', category_id='C1', tags=['running'], tag_vector={'running': 1}, price=99, cost_price=50, gross_margin=0.5, status='active', selection_score=0.86, product_layer='hot', operation_advice=['increase_exposure']),
            Product(id='P2', tenant_id='T1', merchant_id='M1', name='Summer Tee', category_id='C2', tags=['summer'], tag_vector={'summer': 1}, price=49, cost_price=20, gross_margin=0.4, status='active', selection_score=0.62, product_layer='potential', operation_advice=['optimize_detail_page']),
        ])
        db.session.add_all([
            Inventory(tenant_id='T1', merchant_id='M1', product_id='P1', available_stock=20, locked_stock=2, in_transit_stock=0, safe_stock=5),
            Inventory(tenant_id='T1', merchant_id='M1', product_id='P2', available_stock=1, locked_stock=1, in_transit_stock=0, safe_stock=5),
        ])
        db.session.add_all([
            UserProfile(tenant_id='T1', merchant_id='M1', user_id='U1', tag_vector={'running': 3}, category_preference={'C1': 2}, price_preference={'min': 49, 'max': 99, 'avg': 74, 'count': 2}, user_stage='strong_intent'),
            UserProfile(tenant_id='T1', merchant_id='M1', user_id='U2', tag_vector={'summer': 1}, category_preference={'C2': 1}, price_preference={'min': 39, 'max': 49, 'avg': 44, 'count': 2}, user_stage='new'),
        ])
        db.session.add_all([
            RecommendationFeedback(tenant_id='T1', merchant_id='M1', request_id='REQ_REC', event_id='FB1', user_id='U1', product_id='P1', scene='home', feedback_type='exposure', click_flag=False, add_cart_flag=False, convert_flag=False),
            RecommendationFeedback(tenant_id='T1', merchant_id='M1', request_id='REQ_REC', event_id='FB2', user_id='U1', product_id='P1', scene='home', feedback_type='click', click_flag=True, add_cart_flag=False, convert_flag=False),
            RecommendationFeedback(tenant_id='T1', merchant_id='M1', request_id='REQ_REC', event_id='FB3', user_id='U1', product_id='P1', scene='home', feedback_type='add_cart', click_flag=False, add_cart_flag=True, convert_flag=False),
        ])
        db.session.commit()


def test_dashboard_overview_returns_kpis(client, app):
    _seed_dashboard_data(app)

    response = client.get('/api/dashboard/overview', query_string={
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ_DASH_1',
        'scene': 'home',
    })
    assert response.status_code == 200
    body = response.get_json()
    assert body['success'] is True
    assert body['data']['kpis']['behavior_events'] >= 1
    assert body['data']['kpis']['recommendation_requests'] >= 1
    assert 'ctr' in body['data']['kpis']


def test_dashboard_inventory_health_returns_risk_products(client, app):
    _seed_dashboard_data(app)

    response = client.get('/api/dashboard/inventory-health', query_string={
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ_DASH_2',
    })
    assert response.status_code == 200
    body = response.get_json()
    assert body['success'] is True
    assert body['data']['summary']['total_products'] >= 2
    assert any(item['risk_level'] in ('low_stock', 'out_of_stock', 'status_or_score') for item in body['data']['risk_products'])
