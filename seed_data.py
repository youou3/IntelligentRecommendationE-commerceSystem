from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.core.database import db, get_mongo_db
import app.models  # noqa: F401
from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.recommendation_feedback import RecommendationFeedback
from app.models.user import User
from app.models.user_profile import UserProfile


TENANT_ID = 'T1'
MERCHANT_ID = 'M1'


def _assign(obj, **fields):
    for key, value in fields.items():
        setattr(obj, key, value)
    return obj


def seed_mysql():
    now = datetime.utcnow()
    db.session.query(OrderItem).filter_by(tenant_id=TENANT_ID, merchant_id=MERCHANT_ID).delete()
    db.session.query(Order).filter_by(tenant_id=TENANT_ID, merchant_id=MERCHANT_ID).delete()
    db.session.query(RecommendationFeedback).filter_by(tenant_id=TENANT_ID, merchant_id=MERCHANT_ID).delete()
    db.session.query(Inventory).filter_by(tenant_id=TENANT_ID, merchant_id=MERCHANT_ID).delete()
    db.session.query(UserProfile).filter_by(tenant_id=TENANT_ID, merchant_id=MERCHANT_ID).delete()
    db.session.query(User).filter_by(tenant_id=TENANT_ID, merchant_id=MERCHANT_ID).delete()
    db.session.query(Product).filter_by(tenant_id=TENANT_ID, merchant_id=MERCHANT_ID).delete()

    products = [
        _assign(Product(),
            id='P10001', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, name='Running Shoes', category_id='C10001',
            tags=['running', 'summer'], tag_vector={'running': 1, 'summer': 1}, price=99, cost_price=50, gross_margin=0.49,
            status='active', selection_score=0.92, product_layer='hot', operation_advice=['increase_exposure', 'maintain_inventory'], created_at=now - timedelta(days=10),
        ),
        _assign(Product(),
            id='P10002', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, name='Summer Tee', category_id='C10002',
            tags=['summer', 'lightweight'], tag_vector={'summer': 1, 'lightweight': 1}, price=49, cost_price=20, gross_margin=0.59,
            status='active', selection_score=0.72, product_layer='potential', operation_advice=['optimize_detail_page', 'consider_promotion'], created_at=now - timedelta(days=6),
        ),
        _assign(Product(),
            id='P10003', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, name='Winter Jacket', category_id='C10003',
            tags=['winter', 'warm'], tag_vector={'winter': 1, 'warm': 1}, price=199, cost_price=130, gross_margin=0.35,
            status='active', selection_score=0.22, product_layer='risk', operation_advice=['restock_or_hide'], created_at=now - timedelta(days=24),
        ),
        _assign(Product(),
            id='P10004', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, name='Sport Socks', category_id='C10004',
            tags=['sport'], tag_vector={'sport': 1}, price=19, cost_price=6, gross_margin=0.68,
            status='inactive', selection_score=0.18, product_layer='risk', operation_advice=['check_product_status'], created_at=now - timedelta(days=30),
        ),
        _assign(Product(),
            id='P10005', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, name='Outdoor Backpack', category_id='C10005',
            tags=['outdoor', 'travel'], tag_vector={'outdoor': 1, 'travel': 1}, price=129, cost_price=60, gross_margin=0.53,
            status='active', selection_score=0.81, product_layer='hot', operation_advice=['increase_exposure'], created_at=now - timedelta(days=3),
        ),
        _assign(Product(),
            id='P10006', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, name='Yoga Mat', category_id='C10006',
            tags=['fitness', 'home'], tag_vector={'fitness': 1, 'home': 1}, price=59, cost_price=22, gross_margin=0.62,
            status='active', selection_score=0.64, product_layer='potential', operation_advice=['consider_promotion'], created_at=now - timedelta(days=2),
        ),
        _assign(Product(),
            id='P10007', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, name='Thermal Gloves', category_id='C10003',
            tags=['winter', 'gloves'], tag_vector={'winter': 1, 'gloves': 1}, price=39, cost_price=15, gross_margin=0.61,
            status='active', selection_score=0.41, product_layer='long_tail', operation_advice=['test_small_traffic'], created_at=now - timedelta(days=18),
        ),
        _assign(Product(),
            id='P10008', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, name='Casual Hat', category_id='C10007',
            tags=['casual', 'sun'], tag_vector={'casual': 1, 'sun': 1}, price=29, cost_price=8, gross_margin=0.72,
            status='active', selection_score=0.58, product_layer='potential', operation_advice=['optimize_detail_page'], created_at=now - timedelta(days=4),
        ),
    ]

    inventories = [
        _assign(Inventory(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, product_id='P10001', available_stock=20, locked_stock=2, in_transit_stock=0, safe_stock=5),
        _assign(Inventory(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, product_id='P10002', available_stock=9, locked_stock=1, in_transit_stock=0, safe_stock=8),
        _assign(Inventory(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, product_id='P10003', available_stock=0, locked_stock=0, in_transit_stock=0, safe_stock=5),
        _assign(Inventory(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, product_id='P10004', available_stock=3, locked_stock=1, in_transit_stock=0, safe_stock=5),
        _assign(Inventory(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, product_id='P10005', available_stock=32, locked_stock=4, in_transit_stock=0, safe_stock=10),
        _assign(Inventory(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, product_id='P10006', available_stock=14, locked_stock=2, in_transit_stock=3, safe_stock=8),
        _assign(Inventory(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, product_id='P10007', available_stock=5, locked_stock=3, in_transit_stock=0, safe_stock=6),
        _assign(Inventory(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, product_id='P10008', available_stock=18, locked_stock=2, in_transit_stock=0, safe_stock=4),
    ]

    users = [
        _assign(User(), id='U10001', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, nickname='Alice', channel='app', member_level='vip'),
        _assign(User(), id='U10002', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, nickname='Bob', channel='web', member_level='silver'),
        _assign(User(), id='U10003', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, nickname='Cindy', channel='miniapp', member_level='gold'),
        _assign(User(), id='U10004', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, nickname='David', channel='app', member_level='bronze'),
    ]

    profiles = [
        _assign(UserProfile(),
            tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, user_id='U10001',
            tag_vector={'running': 4.0, 'summer': 2.0, 'travel': 1.0}, category_preference={'C10001': 3.0, 'C10005': 2.0},
            price_preference={'min': 49, 'max': 129, 'avg': 89, 'count': 3}, user_stage='strong_intent'
        ),
        _assign(UserProfile(),
            tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, user_id='U10002',
            tag_vector={'winter': 2.0, 'warm': 1.0, 'gloves': 1.0}, category_preference={'C10003': 2.0},
            price_preference={'min': 39, 'max': 199, 'avg': 119, 'count': 3}, user_stage='new'
        ),
        _assign(UserProfile(),
            tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, user_id='U10003',
            tag_vector={'fitness': 3.0, 'home': 2.0, 'casual': 1.0}, category_preference={'C10006': 3.0, 'C10007': 1.0},
            price_preference={'min': 29, 'max': 59, 'avg': 44, 'count': 2}, user_stage='active_browsing'
        ),
        _assign(UserProfile(),
            tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, user_id='U10004',
            tag_vector={'outdoor': 1.0, 'travel': 1.0}, category_preference={'C10005': 1.0},
            price_preference={'min': 129, 'max': 129, 'avg': 129, 'count': 1}, user_stage='converted'
        ),
    ]

    orders = [
        _assign(Order(), id='O10001', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, user_id='U10001', order_status='paid', pay_status='paid', total_amount=198),
        _assign(Order(), id='O10002', tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, user_id='U10003', order_status='paid', pay_status='paid', total_amount=178),
    ]

    order_items = [
        _assign(OrderItem(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, order_id='O10001', product_id='P10001', quantity=1, price=99, amount=99),
        _assign(OrderItem(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, order_id='O10001', product_id='P10002', quantity=2, price=49, amount=98),
        _assign(OrderItem(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, order_id='O10002', product_id='P10006', quantity=2, price=59, amount=118),
        _assign(OrderItem(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, order_id='O10002', product_id='P10008', quantity=2, price=30, amount=60),
    ]

    feedback = [
        _assign(RecommendationFeedback(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, request_id='REQ_SEED_1', event_id='FB_SEED_1', user_id='U10001', product_id='P10001', scene='home', feedback_type='exposure', click_flag=False, add_cart_flag=False, convert_flag=False, created_at=now - timedelta(days=1)),
        _assign(RecommendationFeedback(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, request_id='REQ_SEED_1', event_id='FB_SEED_2', user_id='U10001', product_id='P10001', scene='home', feedback_type='click', click_flag=True, add_cart_flag=False, convert_flag=False, created_at=now - timedelta(days=1)),
        _assign(RecommendationFeedback(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, request_id='REQ_SEED_1', event_id='FB_SEED_3', user_id='U10001', product_id='P10002', scene='detail', feedback_type='add_cart', click_flag=False, add_cart_flag=True, convert_flag=False, created_at=now - timedelta(days=2)),
        _assign(RecommendationFeedback(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, request_id='REQ_SEED_1', event_id='FB_SEED_4', user_id='U10001', product_id='P10001', scene='home', feedback_type='convert', click_flag=False, add_cart_flag=False, convert_flag=True, created_at=now - timedelta(days=1)),
        _assign(RecommendationFeedback(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, request_id='REQ_SEED_2', event_id='FB_SEED_5', user_id='U10003', product_id='P10006', scene='home', feedback_type='exposure', click_flag=False, add_cart_flag=False, convert_flag=False, created_at=now - timedelta(days=3)),
        _assign(RecommendationFeedback(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, request_id='REQ_SEED_2', event_id='FB_SEED_6', user_id='U10003', product_id='P10006', scene='home', feedback_type='click', click_flag=True, add_cart_flag=False, convert_flag=False, created_at=now - timedelta(days=3)),
        _assign(RecommendationFeedback(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, request_id='REQ_SEED_2', event_id='FB_SEED_7', user_id='U10003', product_id='P10006', scene='home', feedback_type='add_cart', click_flag=False, add_cart_flag=True, convert_flag=False, created_at=now - timedelta(days=2)),
        _assign(RecommendationFeedback(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, request_id='REQ_SEED_2', event_id='FB_SEED_8', user_id='U10003', product_id='P10008', scene='detail', feedback_type='exposure', click_flag=False, add_cart_flag=False, convert_flag=False, created_at=now - timedelta(days=1)),
        _assign(RecommendationFeedback(), tenant_id=TENANT_ID, merchant_id=MERCHANT_ID, request_id='REQ_SEED_2', event_id='FB_SEED_9', user_id='U10003', product_id='P10008', scene='detail', feedback_type='click', click_flag=True, add_cart_flag=False, convert_flag=False, created_at=now - timedelta(days=1)),
    ]

    db.session.add_all(products + inventories + users + profiles + orders + order_items + feedback)
    db.session.commit()


def seed_mongo():
    mongo_db = get_mongo_db()
    if mongo_db is None:
        return
    now = datetime.utcnow()
    mongo_db.behavior_events.delete_many({'tenant_id': TENANT_ID, 'merchant_id': MERCHANT_ID})
    mongo_db.recommendation_logs.delete_many({'tenant_id': TENANT_ID, 'merchant_id': MERCHANT_ID})
    mongo_db.behavior_events.insert_many([
        {
            'tenant_id': TENANT_ID,
            'merchant_id': MERCHANT_ID,
            'event_id': 'EVT_SEED_1',
            'request_id': 'REQ_SEED_1',
            'event_type': 'product_click',
            'scene': 'home',
            'user_id': 'U10001',
            'product_id': 'P10001',
            'category_id': 'C10001',
            'tags': ['running', 'summer'],
            'source': 'home_recommend',
            'duration': 18,
            'payload': {},
            'created_at': now - timedelta(days=1),
        },
        {
            'tenant_id': TENANT_ID,
            'merchant_id': MERCHANT_ID,
            'event_id': 'EVT_SEED_2',
            'request_id': 'REQ_SEED_2',
            'event_type': 'add_cart',
            'scene': 'detail',
            'user_id': 'U10001',
            'product_id': 'P10002',
            'category_id': 'C10002',
            'tags': ['summer', 'lightweight'],
            'source': 'detail_page',
            'duration': 25,
            'payload': {'price': 49},
            'created_at': now - timedelta(days=2),
        },
        {
            'tenant_id': TENANT_ID,
            'merchant_id': MERCHANT_ID,
            'event_id': 'EVT_SEED_3',
            'request_id': 'REQ_SEED_3',
            'event_type': 'product_view',
            'scene': 'home',
            'user_id': 'U10003',
            'product_id': 'P10006',
            'category_id': 'C10006',
            'tags': ['fitness', 'home'],
            'source': 'home_recommend',
            'duration': 12,
            'payload': {'price': 59},
            'created_at': now - timedelta(days=3),
        },
        {
            'tenant_id': TENANT_ID,
            'merchant_id': MERCHANT_ID,
            'event_id': 'EVT_SEED_4',
            'request_id': 'REQ_SEED_4',
            'event_type': 'purchase',
            'scene': 'detail',
            'user_id': 'U10004',
            'product_id': 'P10005',
            'category_id': 'C10005',
            'tags': ['outdoor', 'travel'],
            'source': 'detail_page',
            'duration': 30,
            'payload': {'price': 129},
            'created_at': now - timedelta(days=4),
        },
        {
            'tenant_id': TENANT_ID,
            'merchant_id': MERCHANT_ID,
            'event_id': 'EVT_SEED_5',
            'request_id': 'REQ_SEED_5',
            'event_type': 'favorite',
            'scene': 'detail',
            'user_id': 'U10003',
            'product_id': 'P10008',
            'category_id': 'C10007',
            'tags': ['casual', 'sun'],
            'source': 'detail_page',
            'duration': 14,
            'payload': {'price': 29},
            'created_at': now - timedelta(days=5),
        },
    ])
    mongo_db.recommendation_logs.insert_many([
        {
            'tenant_id': TENANT_ID,
            'merchant_id': MERCHANT_ID,
            'request_id': 'REQ_SEED_1',
            'user_id': 'U10001',
            'scene': 'home',
            'recommended_products': ['P10001', 'P10002', 'P10005'],
            'clicked_products': ['P10001'],
            'converted_products': ['P10001'],
            'created_at': now - timedelta(days=1),
        },
        {
            'tenant_id': TENANT_ID,
            'merchant_id': MERCHANT_ID,
            'request_id': 'REQ_SEED_2',
            'user_id': 'U10003',
            'scene': 'detail',
            'recommended_products': ['P10006', 'P10008'],
            'clicked_products': ['P10006'],
            'converted_products': [],
            'created_at': now - timedelta(days=2),
        },
        {
            'tenant_id': TENANT_ID,
            'merchant_id': MERCHANT_ID,
            'request_id': 'REQ_SEED_3',
            'user_id': 'U10004',
            'scene': 'cart',
            'recommended_products': ['P10005', 'P10007'],
            'clicked_products': ['P10005'],
            'converted_products': ['P10005'],
            'created_at': now - timedelta(days=3),
        },
    ])


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_mysql()
        seed_mongo()
        print('Seed data created successfully.')
