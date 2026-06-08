from app.core.database import db
from app.models.recommendation_feedback import RecommendationFeedback


ALLOWED_FEEDBACK_TYPES = {'exposure', 'click', 'add_cart', 'convert'}


class FeedbackService:
    def log_feedback(self, payload: dict):
        feedback_type = payload.get('feedback_type')
        if feedback_type not in ALLOWED_FEEDBACK_TYPES:
            return {'error': 'invalid feedback_type', 'status_code': 400}

        exists = RecommendationFeedback.query.filter_by(
            tenant_id=payload.get('tenant_id'),
            merchant_id=payload.get('merchant_id'),
            event_id=payload.get('event_id'),
        ).first()
        if exists:
            return {'accepted': True, 'duplicate': True, 'event_id': payload.get('event_id')}

        feedback = RecommendationFeedback(
            tenant_id=payload.get('tenant_id'),
            merchant_id=payload.get('merchant_id'),
            request_id=payload.get('request_id'),
            event_id=payload.get('event_id'),
            user_id=payload.get('user_id'),
            product_id=payload.get('product_id'),
            scene=payload.get('scene'),
            feedback_type=feedback_type,
            click_flag=feedback_type == 'click',
            add_cart_flag=feedback_type == 'add_cart',
            convert_flag=feedback_type == 'convert',
        )
        db.session.add(feedback)
        db.session.commit()
        return {'accepted': True, 'duplicate': False, 'event_id': payload.get('event_id')}
