from app.core.database import db
from app.models.tenant_mixin import TenantMixin


class UserProfile(TenantMixin, db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(64), nullable=False, index=True)
    tag_vector = db.Column(db.JSON, nullable=True)
    price_preference = db.Column(db.JSON, nullable=True)
    category_preference = db.Column(db.JSON, nullable=True)
    user_stage = db.Column(db.String(64), nullable=False, default='new')
