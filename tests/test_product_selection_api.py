from app.core.database import db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_selection import ProductSelectionSnapshot
from app.models.recommendation_feedback import RecommendationFeedback


def test_selection_score_endpoint_scores_requested_products(client, app):
    with app.app_context():
        db.session.add(Product(
            id='P1', tenant_id='T1', merchant_id='M1', name='Running Shoes', category_id='C1',
            tags=['running'], price=99, cost_price=50, gross_margin=0.5, status='active'
        ))
        db.session.add(Inventory(
            tenant_id='T1', merchant_id='M1', product_id='P1', available_stock=20, locked_stock=2, in_transit_stock=0, safe_stock=5
        ))
        db.session.add(RecommendationFeedback(
            tenant_id='T1', merchant_id='M1', request_id='REQX', event_id='FBX', user_id='U1', product_id='P1', scene='home', feedback_type='exposure'
        ))
        db.session.commit()

    response = client.post('/api/products/selection-score', json={
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ_SELECTION_1',
        'product_ids': ['P1'],
        'persist': True,
    })
    assert response.status_code == 200
    body = response.get_json()
    assert body['success'] is True
    assert body['data']['items'][0]['product_id'] == 'P1'
    assert 'selection_score' in body['data']['items'][0]
    assert 'layer' in body['data']['items'][0]

    with app.app_context():
        assert ProductSelectionSnapshot.query.filter_by(tenant_id='T1', merchant_id='M1', request_id='REQ_SELECTION_1', product_id='P1').count() == 1
        product = Product.query.filter_by(tenant_id='T1', merchant_id='M1', id='P1').first()
        assert product.selection_score is not None
        assert product.product_layer is not None


def test_selection_score_requires_tenant_merchant_request(client):
    response = client.post('/api/products/selection-score', json={'tenant_id': 'T1', 'merchant_id': 'M1'})
    assert response.status_code == 400
