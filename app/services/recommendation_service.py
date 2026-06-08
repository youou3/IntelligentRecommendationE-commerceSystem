from datetime import datetime

from app.core.database import db, get_mongo_db
from app.models.product import Product
from app.models.recommendation_feedback import RecommendationFeedback
from app.models.user_profile import UserProfile
from app.skills.recommendation_skill import RecommendationSkill


class RecommendationService:
    skill = RecommendationSkill()

    def recommend(self, tenant_id: str, merchant_id: str, user_id: str, scene: str, limit: int, request_id: str):
        mongo_db = get_mongo_db()
        if mongo_db is None:
            return {'error': 'mongo unavailable', 'status_code': 503}

        profile = UserProfile.query.filter_by(
            tenant_id=tenant_id,
            merchant_id=merchant_id,
            user_id=user_id,
        ).first()
        profile_tags = profile.tag_vector if profile and profile.tag_vector else {}
        preferred_categories = profile.category_preference if profile and profile.category_preference else {}

        products = Product.query.filter_by(
            tenant_id=tenant_id,
            merchant_id=merchant_id,
            status='active',
        ).order_by(Product.created_at.desc()).all()

        product_items = []
        for product in products:
            product_items.append({
                'product_id': product.id,
                'name': product.name,
                'category_id': product.category_id,
                'tags': product.tags or [],
                'price': str(product.price),
                'gross_margin': str(product.gross_margin),
                'created_at': product.created_at.isoformat() if product.created_at else '',
            })

        ranked = self.skill.execute({
            'profile_tags': profile_tags,
            'preferred_categories': preferred_categories,
            'products': product_items,
        })['items']

        ranked = ranked[:limit]
        response_items = []
        recommended_products = []
        for item in ranked:
            product = item['product']
            product_id = product['product_id']
            recommended_products.append(product_id)
            response_items.append({
                'product_id': product_id,
                'name': product['name'],
                'category_id': product['category_id'],
                'tags': product['tags'],
                'score': item['score'],
                'explanation': {
                    'matched_tags': item['matched_tags'],
                    'matched_category': item['matched_category'],
                    'reason': item['reason'],
                },
            })

        mongo_db.recommendation_logs.insert_one({
            'tenant_id': tenant_id,
            'merchant_id': merchant_id,
            'request_id': request_id,
            'user_id': user_id,
            'scene': scene,
            'recommended_products': recommended_products,
            'clicked_products': [],
            'converted_products': [],
            'created_at': datetime.utcnow(),
        })

        for product_id in recommended_products:
            exists = RecommendationFeedback.query.filter_by(
                tenant_id=tenant_id,
                merchant_id=merchant_id,
                event_id=f'{request_id}:exposure:{product_id}',
            ).first()
            if exists is None:
                db.session.add(RecommendationFeedback(
                    tenant_id=tenant_id,
                    merchant_id=merchant_id,
                    request_id=request_id,
                    event_id=f'{request_id}:exposure:{product_id}',
                    user_id=user_id,
                    product_id=product_id,
                    scene=scene,
                    feedback_type='exposure',
                    click_flag=False,
                    add_cart_flag=False,
                    convert_flag=False,
                ))
        db.session.commit()

        return {
            'recommendation_request_id': request_id,
            'items': response_items,
        }
