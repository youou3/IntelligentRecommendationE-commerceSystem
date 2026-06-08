from collections import Counter, defaultdict

from app.skills.base import BaseSkill


EVENT_WEIGHTS = {
    'product_view': 1,
    'product_click': 2,
    'favorite': 3,
    'add_cart': 4,
    'purchase': 6,
}


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

        for event in events:
            event_count += 1
            event_type = event.get('event_type')
            weight = EVENT_WEIGHTS.get(event_type, 1)
            tags = event.get('tags') or []
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
            for tag in tags:
                tag_weights[tag] += weight
            category_id = event.get('category_id')
            if category_id:
                category_weights[category_id] += weight
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

        return {
            'tag_vector': dict(tag_weights),
            'category_preference': dict(category_weights),
            'price_preference': {},
            'user_stage': user_stage,
        }
