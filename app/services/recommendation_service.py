from datetime import datetime, timedelta

from app.core.database import db, get_mongo_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.recommendation_feedback import RecommendationFeedback
from app.models.user_profile import UserProfile
from app.skills.recommendation_skill import RecommendationSkill


class RecommendationService:
    skill = RecommendationSkill()

    def _parse_exclude_ids(self, exclude_product_ids):
        if not exclude_product_ids:
            return set()
        if isinstance(exclude_product_ids, str):
            return {item.strip() for item in exclude_product_ids.split(',') if item.strip()}
        return set(exclude_product_ids)

    def recommend(self, tenant_id: str, merchant_id: str, user_id: str, scene: str, limit: int, request_id: str, exclude_product_ids=None, min_stock: int = 1, dedup_days: int = 7, max_recent_exposures: int = 3):
        mongo_db = get_mongo_db()
        if mongo_db is None:
            return {'error': 'mongo unavailable', 'status_code': 503}

        exclude_ids = self._parse_exclude_ids(exclude_product_ids)
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

        product_ids = [product.id for product in products]
        inventory_rows = Inventory.query.filter(
            Inventory.tenant_id == tenant_id,
            Inventory.merchant_id == merchant_id,
            Inventory.product_id.in_(product_ids),
        ).all() if product_ids else []
        inventory_map = {row.product_id: row for row in inventory_rows}

        recent_cutoff = datetime.utcnow() - timedelta(days=dedup_days)
        recent_exposures = RecommendationFeedback.query.filter(
            RecommendationFeedback.tenant_id == tenant_id,
            RecommendationFeedback.merchant_id == merchant_id,
            RecommendationFeedback.user_id == user_id,
            RecommendationFeedback.feedback_type == 'exposure',
            RecommendationFeedback.created_at >= recent_cutoff,
        ).all()
        exposure_counts = {}
        for row in recent_exposures:
            exposure_counts[row.product_id] = exposure_counts.get(row.product_id, 0) + 1

        feedback_counts = RecommendationFeedback.query.filter(
            RecommendationFeedback.tenant_id == tenant_id,
            RecommendationFeedback.merchant_id == merchant_id,
            RecommendationFeedback.feedback_type.in_(['click', 'add_cart', 'convert']),
        ).all()
        feedback_map = {}
        for row in feedback_counts:
            feedback_map.setdefault(row.product_id, {'click': 0, 'add_cart': 0, 'convert': 0})
            feedback_map[row.product_id][row.feedback_type] += 1

        product_items = []
        for product in products:
            if product.id in exclude_ids:
                continue
            inventory_row = inventory_map.get(product.id)
            available_stock = inventory_row.available_stock if inventory_row else 100
            locked_stock = inventory_row.locked_stock if inventory_row else 0
            effective_stock = available_stock - locked_stock
            if inventory_row and effective_stock < min_stock:
                continue
            if exposure_counts.get(product.id, 0) >= max_recent_exposures:
                continue
            feedback_stat = feedback_map.get(product.id, {'click': 0, 'add_cart': 0, 'convert': 0})
            product_items.append({
                'product_id': product.id,
                'name': product.name,
                'category_id': product.category_id,
                'tags': product.tags or [],
                'tag_vector': product.tag_vector,
                'price': str(product.price),
                'gross_margin': str(product.gross_margin),
                'created_at': product.created_at.isoformat() if product.created_at else '',
                'available_stock': available_stock,
                'locked_stock': locked_stock,
                'effective_stock': effective_stock,
                'popularity_score': min((feedback_stat['click'] + 2 * feedback_stat['add_cart'] + 3 * feedback_stat['convert']) / 20.0, 1.0),
                'feedback_count': feedback_stat['click'] + feedback_stat['add_cart'] + feedback_stat['convert'],
            })

        ranked_result = self.skill.execute({
            'profile_tags': profile_tags,
            'preferred_categories': preferred_categories,
            'products': product_items,
        })
        ranked = ranked_result['items'][:limit]
        strategy = ranked_result.get('strategy', 'cosine_similarity')
        cold_start = ranked_result.get('cold_start', False)
        if not ranked and product_items:
            ranked = self.skill.execute({
                'profile_tags': {},
                'preferred_categories': {},
                'products': product_items,
                'strategy': 'cold_start_popularity',
            })['items'][:limit]
            strategy = 'cold_start_fallback'
            cold_start = True

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
                'inventory': {
                    'available_stock': product['available_stock'],
                    'locked_stock': product['locked_stock'],
                    'effective_stock': product['effective_stock'],
                },
                'explanation': {
                    'matched_tags': item['matched_tags'],
                    'matched_category': item['matched_category'],
                    'cosine_similarity': item['cosine_similarity'],
                    'category_score': item['category_score'],
                    'margin_score': item['margin_score'],
                    'freshness_score': item['freshness_score'],
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

        if not response_items and product_items:
            fallback_items = sorted(product_items, key=lambda p: (p['popularity_score'], p['effective_stock'], p['created_at']), reverse=True)[:limit]
            response_items = [{
                'product_id': item['product_id'],
                'name': item['name'],
                'category_id': item['category_id'],
                'tags': item['tags'],
                'score': 0.0,
                'inventory': {
                    'available_stock': item['available_stock'],
                    'locked_stock': item['locked_stock'],
                    'effective_stock': item['effective_stock'],
                },
                'explanation': {
                    'matched_tags': [],
                    'matched_category': False,
                    'cosine_similarity': 0.0,
                    'category_score': 0.0,
                    'margin_score': 0.0,
                    'freshness_score': 0.0,
                    'reason': 'cold_start_fallback',
                },
            } for item in fallback_items]
            strategy = 'cold_start_fallback'
            cold_start = True

        return {
            'recommendation_request_id': request_id,
            'items': response_items,
            'strategy': strategy,
            'cold_start': cold_start,
        }
