from collections import Counter
from datetime import datetime, timezone

from app.skills.base import BaseSkill


EVENT_WEIGHTS = {
    'product_view': 1.0,
    'product_click': 2.0,
    'favorite': 3.0,
    'add_cart': 4.0,
    'purchase': 6.0,
}


def _recency_decay(created_at):
    if not created_at:
        return 1.0
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        except ValueError:
            return 1.0
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    age_days = (now - created_at.astimezone(timezone.utc)).days
    if age_days <= 1:
        return 1.0
    if age_days <= 7:
        return 0.8
    if age_days <= 30:
        return 0.5
    return 0.2


class UserProfileSkill(BaseSkill):
    name = 'user_profile'

    def validate(self, payload: dict) -> bool:
        return bool(payload.get('events'))

    def execute(self, payload: dict) -> dict:
        events = payload.get('events') or []
        tag_weights = Counter()
        category_weights = Counter()
        event_count = 0
        has_add_cart = False
        has_purchase = False
        has_favorite = False
        prices = []

        for event in events:
            event_count += 1
            event_type = event.get('event_type')
            weight = EVENT_WEIGHTS.get(event_type, 1.0)
            weight *= _recency_decay(event.get('created_at'))
            tags = event.get('tags') or []
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
            for tag in tags:
                tag_weights[tag] += weight
            category_id = event.get('category_id')
            if category_id:
                category_weights[category_id] += weight
            price = event.get('price')
            if price is None and isinstance(event.get('payload'), dict):
                price = event['payload'].get('price')
            if price is not None:
                try:
                    prices.append(float(price))
                except (TypeError, ValueError):
                    pass
            if event_type == 'add_cart':
                has_add_cart = True
            elif event_type == 'purchase':
                has_purchase = True
            elif event_type == 'favorite':
                has_favorite = True

        if has_purchase:
            user_stage = 'converted'
        elif has_add_cart or has_favorite:
            user_stage = 'strong_intent'
        elif event_count < 3:
            user_stage = 'new'
        else:
            user_stage = 'active_browsing'

        if prices:
            price_preference = {
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices),
                'count': len(prices),
            }
        else:
            price_preference = {}

        return {
            'tag_vector': dict(tag_weights),
            'category_preference': dict(category_weights),
            'price_preference': price_preference,
            'user_stage': user_stage,
        }
