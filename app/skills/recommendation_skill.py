from app.skills.base import BaseSkill


class RecommendationSkill(BaseSkill):
    name = 'recommendation'

    def validate(self, payload: dict) -> bool:
        return bool(payload.get('products'))

    def execute(self, payload: dict) -> dict:
        profile_tags = payload.get('profile_tags') or {}
        preferred_categories = payload.get('preferred_categories') or {}
        products = payload.get('products') or []
        ranked = []

        for product in products:
            tags = product.get('tags') or []
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
            score = 0
            matched_tags = []
            for tag in tags:
                if tag in profile_tags:
                    score += profile_tags[tag]
                    matched_tags.append(tag)
            category_id = product.get('category_id')
            matched_category = bool(category_id and category_id in preferred_categories)
            if matched_category:
                score += preferred_categories[category_id]
            ranked.append({
                'product': product,
                'score': score,
                'matched_tags': matched_tags,
                'matched_category': matched_category,
                'reason': 'Matched user interests: ' + ', '.join(matched_tags) if matched_tags else 'fallback_active_product',
            })

        ranked.sort(key=lambda item: (item['score'], item['product'].get('created_at') or ''), reverse=True)
        return {'items': ranked}
