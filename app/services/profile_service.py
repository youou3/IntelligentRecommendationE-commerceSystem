from app.core.database import db, get_mongo_db
from app.core.validation import require_fields
from app.models.user_profile import UserProfile
from app.skills.user_profile_skill import UserProfileSkill


class ProfileService:
    skill = UserProfileSkill()

    def generate_profile(self, tenant_id: str, merchant_id: str, user_id: str):
        mongo_db = get_mongo_db()
        if mongo_db is None:
            return {'error': 'mongo unavailable', 'status_code': 503}

        events = list(mongo_db.behavior_events.find({
            'tenant_id': tenant_id,
            'merchant_id': merchant_id,
            'user_id': user_id,
        }).sort('created_at', 1))

        result = self.skill.execute({'events': events})
        profile = UserProfile.query.filter_by(
            tenant_id=tenant_id,
            merchant_id=merchant_id,
            user_id=user_id,
        ).first()

        if profile is None:
            profile = UserProfile(
                tenant_id=tenant_id,
                merchant_id=merchant_id,
                user_id=user_id,
            )
            db.session.add(profile)

        profile.tag_vector = result['tag_vector']
        profile.category_preference = result['category_preference']
        profile.price_preference = result['price_preference']
        profile.user_stage = result['user_stage']
        db.session.commit()

        return {
            'user_id': user_id,
            'tag_vector': result['tag_vector'],
            'category_preference': result['category_preference'],
            'price_preference': result['price_preference'],
            'user_stage': result['user_stage'],
        }
