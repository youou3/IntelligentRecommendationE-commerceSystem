from app.skills.base import BaseSkill


class BehaviorCollectSkill(BaseSkill):
    name = 'behavior_collect'

    def validate(self, payload: dict) -> bool:
        required = ['tenant_id', 'merchant_id', 'request_id', 'event_id', 'user_id', 'event_type']
        return all(payload.get(field) not in (None, '') for field in required)

    def execute(self, payload: dict) -> dict:
        tags = payload.get('tags') or []
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        return {
            'tenant_id': payload.get('tenant_id'),
            'merchant_id': payload.get('merchant_id'),
            'request_id': payload.get('request_id'),
            'event_id': payload.get('event_id'),
            'user_id': payload.get('user_id'),
            'event_type': payload.get('event_type'),
            'product_id': payload.get('product_id'),
            'category_id': payload.get('category_id'),
            'tags': tags,
            'source': payload.get('source'),
            'duration': payload.get('duration'),
            'scene': payload.get('scene'),
            'payload': payload.get('payload') or {},
        }
