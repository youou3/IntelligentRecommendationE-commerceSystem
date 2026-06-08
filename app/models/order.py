from app.core.database import db
from app.models.tenant_mixin import TenantMixin


class Order(TenantMixin, db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64), nullable=False, index=True)
    order_status = db.Column(db.String(32), nullable=False, default='created')
    pay_status = db.Column(db.String(32), nullable=False, default='unpaid')
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)


class OrderItem(TenantMixin, db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(64), nullable=False, index=True)
    product_id = db.Column(db.String(64), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
