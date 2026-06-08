from datetime import datetime

from app.core.database import db, get_mongo_db
from app.core.validation import require_fields
from app.skills.behavior_collect_skill import BehaviorCollectSkill


class BehaviorService:
    skill = BehaviorCollectSkill()

    def collect_behavior(self, payload: dict):
        missing = require_fields(payload, ['tenant_id', 'merchant_id', 'request_id', 'event_id', 'user_id', 'event_type'])
        if missing:
            return {'error': f'missing fields: {", ".join(missing)}', 'status_code': 400}

        mongo_db = get_mongo_db()
        if mongo_db is None:
            return {'error': 'mongo unavailable', 'status_code': 503}

        document = self.skill.execute(payload)
        document['created_at'] = datetime.utcnow()

        existing = mongo_db.behavior_events.find_one({
            'tenant_id': document['tenant_id'],
            'merchant_id': document['merchant_id'],
            'event_id': document['event_id'],
        })
        if existing:
            return {'accepted': True, 'duplicate': True, 'event_id': document['event_id']}

        mongo_db.behavior_events.insert_one(document)
        return {'accepted': True, 'duplicate': False, 'event_id': document['event_id']}
