from app.core.database import db
from app.models.tenant_mixin import TenantMixin


class User(TenantMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(64), primary_key=True)
    nickname = db.Column(db.String(128), nullable=False)
    channel = db.Column(db.String(64), nullable=True)
    member_level = db.Column(db.String(64), nullable=True)
