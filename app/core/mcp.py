from datetime import datetime
from time import perf_counter
from uuid import uuid4

from app.core.database import get_mongo_db


class SkillNotFoundError(Exception):
    pass


class SkillValidationError(Exception):
    pass


class SkillRegistry:
    def __init__(self):
        self._skills = {}

    def register(self, skill):
        name = getattr(skill, 'name', '')
        version = getattr(skill, 'version', '1.0.0')
        if not name:
            raise ValueError('skill name is required')
        self._skills[(name, version)] = skill
        self._skills[(name, None)] = skill
        return skill

    def get(self, name, version=None):
        skill = self._skills.get((name, version))
        if skill is None:
            raise SkillNotFoundError(f'skill not found: {name}@{version or "latest"}')
        return skill

    def list_skills(self):
        rows = []
        seen = set()
        for (name, version), skill in self._skills.items():
            if version is None or (name, version) in seen:
                continue
            seen.add((name, version))
            rows.append({
                'name': name,
                'version': version,
                'class_name': skill.__class__.__name__,
            })
        return sorted(rows, key=lambda row: (row['name'], row['version']))


class MCPDispatcher:
    def __init__(self, registry):
        self.registry = registry
        self.fallbacks = {}

    def register_fallback(self, skill_name, fallback):
        self.fallbacks[skill_name] = fallback

    def call(self, skill_name, payload, tenant_id=None, merchant_id=None, request_id=None, version=None, fallback_payload=None):
        skill = self.registry.get(skill_name, version)
        tenant_id = tenant_id if tenant_id is not None else payload.get('tenant_id')
        merchant_id = merchant_id if merchant_id is not None else payload.get('merchant_id')
        request_id = request_id if request_id is not None else payload.get('request_id') or f'REQ-{uuid4().hex[:12]}'
        started = perf_counter()
        status = 'success'
        error_message = None
        output_payload = None
        fallback_used = False

        try:
            if not skill.validate(payload):
                raise SkillValidationError(f'invalid payload for skill: {skill_name}')
            output_payload = skill.execute(payload)
            return self._standard_response(output_payload, request_id, fallback_used=False)
        except Exception as exc:
            status = 'failed'
            error_message = str(exc)
            fallback = self.fallbacks.get(skill_name)
            if fallback is None:
                raise
            fallback_used = True
            status = 'fallback'
            output_payload = fallback(payload, exc, fallback_payload or {})
            return self._standard_response(output_payload, request_id, code='FALLBACK', message=error_message, fallback_used=True)
        finally:
            cost_ms = int((perf_counter() - started) * 1000)
            self._write_log(
                tenant_id=tenant_id,
                merchant_id=merchant_id,
                skill_name=skill_name,
                skill_version=getattr(skill, 'version', '1.0.0'),
                request_id=request_id,
                input_payload=payload,
                output_payload=output_payload,
                status=status,
                cost_ms=cost_ms,
                error_message=error_message,
                fallback_used=fallback_used,
            )

    def _standard_response(self, data, request_id, code='OK', message='success', fallback_used=False):
        return {
            'success': code in ('OK', 'FALLBACK'),
            'code': code,
            'message': message,
            'request_id': request_id,
            'data': data or {},
            'fallback_used': fallback_used,
        }

    def _write_log(self, tenant_id, merchant_id, skill_name, skill_version, request_id, input_payload, output_payload, status, cost_ms, error_message=None, fallback_used=False):
        mongo_db = get_mongo_db()
        if mongo_db is None:
            return
        mongo_db.skill_call_logs.insert_one({
            'tenant_id': tenant_id,
            'merchant_id': merchant_id,
            'skill_name': skill_name,
            'skill_version': skill_version,
            'request_id': request_id,
            'input_payload': input_payload,
            'output_payload': output_payload or {},
            'status': status,
            'cost_ms': cost_ms,
            'error_message': error_message,
            'fallback_used': fallback_used,
            'created_at': datetime.utcnow(),
        })


skill_registry = SkillRegistry()
mcp_dispatcher = MCPDispatcher(skill_registry)
