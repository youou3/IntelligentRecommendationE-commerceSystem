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


class InventoryLog(TenantMixin, db.Model):
    __tablename__ = 'inventory_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.String(64), nullable=False, index=True)
    change_type = db.Column(db.String(32), nullable=False, index=True)
    change_quantity = db.Column(db.Integer, nullable=False, default=0)
    request_id = db.Column(db.String(64), nullable=True, index=True)
    event_id = db.Column(db.String(64), nullable=True, index=True)
    before_snapshot = db.Column(db.JSON, nullable=True)
    after_snapshot = db.Column(db.JSON, nullable=True)


class InventoryWarning(TenantMixin, db.Model):
    __tablename__ = 'inventory_warnings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.String(64), nullable=False, index=True)
    warning_level = db.Column(db.String(32), nullable=False, index=True)
    warning_reason = db.Column(db.JSON, nullable=False, default=list)
    status = db.Column(db.String(32), nullable=False, default='triggered', index=True)
    request_id = db.Column(db.String(64), nullable=True, index=True)
    forecast_daily_sales = db.Column(db.Numeric(12, 4), nullable=False, default=0)
    stockout_days = db.Column(db.Numeric(12, 4), nullable=True)
    suggested_action = db.Column(db.String(64), nullable=False, default='observe')


class ReplenishmentOrder(TenantMixin, db.Model):
    __tablename__ = 'replenishment_orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.String(64), nullable=False, index=True)
    suggest_quantity = db.Column(db.Integer, nullable=False, default=0)
    approved_quantity = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(32), nullable=False, default='draft', index=True)
    request_id = db.Column(db.String(64), nullable=True, index=True)
    forecast_days = db.Column(db.Integer, nullable=False, default=14)
    reason = db.Column(db.JSON, nullable=False, default=list)
    risk_note = db.Column(db.JSON, nullable=False, default=list)
    source_warning_id = db.Column(db.Integer, nullable=True, index=True)
