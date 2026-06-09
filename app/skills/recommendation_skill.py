import math
from datetime import datetime, timezone

from app.skills.base import BaseSkill


def _to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _freshness_score(created_at):
    if not created_at:
        return 0.0
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        except ValueError:
            return 0.0
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    age_days = (datetime.now(timezone.utc) - created_at.astimezone(timezone.utc)).days
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.5
    return 0.0


class RecommendationSkill(BaseSkill):
    name = 'recommendation'

    def validate(self, payload: dict) -> bool:
        return bool(payload.get('products'))

    def _vectorize_tags(self, tags):
        if not tags:
            return {}
        if isinstance(tags, dict):
            return {str(k): _to_float(v, 0.0) for k, v in tags.items()}
        vector = {}
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        for tag in tags:
            vector[str(tag)] = vector.get(str(tag), 0.0) + 1.0
        return vector

    def _cosine_similarity(self, user_vector, product_vector):
        if not user_vector or not product_vector:
            return 0.0
        dot = 0.0
        for key, user_weight in user_vector.items():
            dot += _to_float(user_weight) * _to_float(product_vector.get(key, 0.0))
        user_norm = math.sqrt(sum(_to_float(v) ** 2 for v in user_vector.values()))
        product_norm = math.sqrt(sum(_to_float(v) ** 2 for v in product_vector.values()))
        if user_norm == 0 or product_norm == 0:
            return 0.0
        return dot / (user_norm * product_norm)

    def execute(self, payload: dict) -> dict:
        profile_tags = payload.get('profile_tags') or {}
        preferred_categories = payload.get('preferred_categories') or {}
        products = payload.get('products') or []
        cold_start = not bool(profile_tags)
        strategy = payload.get('strategy', 'recommendation')
        ranked = []

        for product in products:
            tags = product.get('tags') or []
            product_vector = product.get('tag_vector') or self._vectorize_tags(tags)
            user_vector = profile_tags or {}
            category_id = product.get('category_id')
            gross_margin = _to_float(product.get('gross_margin'), 0.0)
            cosine_similarity = self._cosine_similarity(user_vector, product_vector)
            category_score = min(_to_float(preferred_categories.get(category_id, 0.0)) / 10.0, 1.0) if category_id else 0.0
            margin_score = max(0.0, min(gross_margin, 1.0))
            freshness_score = _freshness_score(product.get('created_at'))
            if cold_start:
                popularity_score = _to_float(product.get('popularity_score'), 0.0)
                inventory_score = min(_to_float(product.get('effective_stock'), 0.0) / 100.0, 1.0)
                score = 0.40 * popularity_score + 0.25 * margin_score + 0.20 * inventory_score + 0.15 * freshness_score
            else:
                score = 0.70 * cosine_similarity + 0.15 * category_score + 0.10 * margin_score + 0.05 * freshness_score
                if _to_float(product.get('feedback_count'), 0.0) == 0.0:
                    score += 0.05
            matched_tags = [tag for tag in product_vector if tag in user_vector]
            matched_category = bool(category_id and category_id in preferred_categories)
            ranked.append({
                'product': product,
                'score': round(score, 4),
                'matched_tags': matched_tags,
                'matched_category': matched_category,
                'cosine_similarity': round(cosine_similarity, 4),
                'category_score': round(category_score, 4),
                'margin_score': round(margin_score, 4),
                'freshness_score': round(freshness_score, 4),
                'reason': 'cosine_similarity_match' if not cold_start else 'cold_start_popularity',
            })

        ranked.sort(key=lambda item: (item['score'], item['product'].get('created_at') or ''), reverse=True)
        return {'items': ranked, 'strategy': strategy, 'cold_start': cold_start}
