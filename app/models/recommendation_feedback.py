from app.core.database import db
from app.models.tenant_mixin import TenantMixin


class RecommendationFeedback(TenantMixin, db.Model):
    __tablename__ = 'recommendation_feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.String(64), nullable=False, index=True)
    event_id = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.String(64), nullable=False, index=True)
    product_id = db.Column(db.String(64), nullable=False, index=True)
    scene = db.Column(db.String(64), nullable=True)
    feedback_type = db.Column(db.String(32), nullable=False)
    click_flag = db.Column(db.Boolean, nullable=False, default=False)
    add_cart_flag = db.Column(db.Boolean, nullable=False, default=False)
    convert_flag = db.Column(db.Boolean, nullable=False, default=False)
