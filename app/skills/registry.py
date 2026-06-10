from app.core.mcp import mcp_dispatcher, skill_registry
from app.skills.behavior_collect_skill import BehaviorCollectSkill
from app.skills.inventory_warning_skill import InventoryWarningSkill
from app.skills.product_selection_skill import ProductSelectionSkill
from app.skills.recommendation_skill import RecommendationSkill
from app.skills.replenishment_skill import ReplenishmentSkill
from app.skills.user_profile_skill import UserProfileSkill


def _empty_items_fallback(payload, exc, fallback_payload):
    return fallback_payload or {'items': []}


def register_default_skills():
    for skill in (
        BehaviorCollectSkill(),
        UserProfileSkill(),
        RecommendationSkill(),
        ProductSelectionSkill(),
        InventoryWarningSkill(),
        ReplenishmentSkill(),
    ):
        skill_registry.register(skill)

    mcp_dispatcher.register_fallback('recommendation', _empty_items_fallback)
    mcp_dispatcher.register_fallback('product_selection', _empty_items_fallback)
    mcp_dispatcher.register_fallback('inventory_warning', _empty_items_fallback)
    mcp_dispatcher.register_fallback('replenishment', lambda payload, exc, fallback_payload: fallback_payload or {
        'product_id': payload.get('product_id'),
        'forecast_days': payload.get('forecast_days') or 14,
        'suggest_quantity': 0,
        'target_stock': 0,
        'effective_stock': max(int(payload.get('available_stock') or 0) - int(payload.get('locked_stock') or 0), 0),
        'daily_sales': 0,
        'action': 'manual_review',
        'reason': ['skill_fallback'],
        'risk_note': [str(exc)],
    })

    return skill_registry
