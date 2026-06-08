from datetime import datetime

from app.core.database import db


class TenantMixin:
    tenant_id = db.Column(db.String(64), nullable=False, index=True)
    merchant_id = db.Column(db.String(64), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
