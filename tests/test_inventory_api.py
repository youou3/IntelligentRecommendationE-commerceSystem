from datetime import datetime, timedelta

from app.core.database import db
from app.models.inventory import Inventory, InventoryLog, InventoryWarning, ReplenishmentOrder
from app.models.order import Order, OrderItem
from app.models.product import Product


def _seed_inventory_data(app):
    with app.app_context():
        now = datetime.utcnow()
        db.session.add(Product(
            id='P_LOW',
            tenant_id='T1',
            merchant_id='M1',
            name='Low Stock Hoodie',
            category_id='C1',
            tags=['hoodie'],
            price=199,
            cost_price=90,
            gross_margin=0.55,
            status='active',
            selection_score=0.7,
            product_layer='hot',
        ))
        db.session.add(Inventory(
            tenant_id='T1',
            merchant_id='M1',
            product_id='P_LOW',
            available_stock=2,
            locked_stock=0,
            in_transit_stock=0,
            safe_stock=5,
        ))
        db.session.add(Order(
            id='O1',
            tenant_id='T1',
            merchant_id='M1',
            user_id='U1',
            order_status='paid',
            pay_status='paid',
            total_amount=398,
            created_at=now - timedelta(days=1),
        ))
        db.session.add(OrderItem(
            tenant_id='T1',
            merchant_id='M1',
            order_id='O1',
            product_id='P_LOW',
            quantity=4,
            price=199,
            amount=796,
            created_at=now - timedelta(days=1),
        ))
        db.session.commit()


def test_inventory_warning_workflow_persists_and_lists_warnings(client, app):
    _seed_inventory_data(app)

    response = client.post('/api/inventory/warnings/run', json={
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ_INV_WARN_1',
        'product_ids': ['P_LOW'],
    })
    assert response.status_code == 200
    body = response.get_json()
    assert body['success'] is True
    assert body['data']['items'][0]['product_id'] == 'P_LOW'
    assert body['data']['items'][0]['warning_level'] in ('critical', 'high')

    with app.app_context():
        assert InventoryWarning.query.filter_by(tenant_id='T1', merchant_id='M1', product_id='P_LOW').count() == 1

    list_response = client.get('/api/inventory/warnings', query_string={
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ_INV_WARN_LIST_1',
        'status': 'triggered',
    })
    assert list_response.status_code == 200
    list_body = list_response.get_json()
    assert list_body['data']['total'] == 1
    assert list_body['data']['items'][0]['product_id'] == 'P_LOW'


def test_replenishment_suggest_creates_order(client, app):
    _seed_inventory_data(app)
    client.post('/api/inventory/warnings/run', json={
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ_INV_WARN_2',
        'product_ids': ['P_LOW'],
    })

    response = client.post('/api/inventory/replenishment/suggest', json={
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ_REPLENISH_1',
        'product_id': 'P_LOW',
        'forecast_days': 14,
    })
    assert response.status_code == 200
    body = response.get_json()
    assert body['success'] is True
    assert body['data']['suggest_quantity'] > 0
    assert body['data']['status'] == 'pending_approval'

    with app.app_context():
        order = ReplenishmentOrder.query.filter_by(tenant_id='T1', merchant_id='M1', request_id='REQ_REPLENISH_1').first()
        assert order is not None
        assert order.product_id == 'P_LOW'


def test_inventory_event_is_idempotent(client, app):
    _seed_inventory_data(app)

    payload = {
        'tenant_id': 'T1',
        'merchant_id': 'M1',
        'request_id': 'REQ_INV_EVENT_1',
        'event_id': 'EVT_STOCK_OUT_1',
        'product_id': 'P_LOW',
        'change_type': 'stock_out',
        'quantity': 1,
    }
    first = client.post('/api/inventory/events', json=payload)
    second = client.post('/api/inventory/events', json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.get_json()['data']['idempotent'] is False
    assert second.get_json()['data']['idempotent'] is True

    with app.app_context():
        inventory = Inventory.query.filter_by(tenant_id='T1', merchant_id='M1', product_id='P_LOW').first()
        assert inventory.available_stock == 1
        assert InventoryLog.query.filter_by(tenant_id='T1', merchant_id='M1', event_id='EVT_STOCK_OUT_1').count() == 1
