from app.core.database import db
from app.models.tenant_mixin import TenantMixin


class ProductSelectionSnapshot(TenantMixin, db.Model):
    __tablename__ = 'product_selection_snapshots'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.String(64), nullable=False, index=True)
    product_id = db.Column(db.String(64), nullable=False, index=True)
    selection_score = db.Column(db.Numeric(8, 4), nullable=False, default=0)
    layer = db.Column(db.String(32), nullable=False)
    metrics = db.Column(db.JSON, nullable=True)
    advice = db.Column(db.JSON, nullable=True)
