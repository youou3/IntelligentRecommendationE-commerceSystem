from app.core.database import db
from app.models.tenant_mixin import TenantMixin


class Product(TenantMixin, db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.String(64), nullable=True)
    tags = db.Column(db.JSON, nullable=True)
    tag_vector = db.Column(db.JSON, nullable=True)
    price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    cost_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    gross_margin = db.Column(db.Numeric(12, 4), nullable=False, default=0)
    status = db.Column(db.String(32), nullable=False, default='active')
    selection_score = db.Column(db.Numeric(8, 4), nullable=False, default=0)
    product_layer = db.Column(db.String(32), nullable=True)
    operation_advice = db.Column(db.JSON, nullable=True)
