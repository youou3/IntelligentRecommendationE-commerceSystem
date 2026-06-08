from app.core.database import db
from app.models.tenant_mixin import TenantMixin


class Inventory(TenantMixin, db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.String(64), nullable=False, index=True)
    available_stock = db.Column(db.Integer, nullable=False, default=0)
    locked_stock = db.Column(db.Integer, nullable=False, default=0)
    in_transit_stock = db.Column(db.Integer, nullable=False, default=0)
    safe_stock = db.Column(db.Integer, nullable=False, default=0)
