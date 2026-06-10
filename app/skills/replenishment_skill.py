from math import ceil

from app.skills.base import BaseSkill


class ReplenishmentSkill(BaseSkill):
    name = 'replenishment'

    def validate(self, payload: dict) -> bool:
        return bool(payload.get('product_id'))

    def execute(self, payload: dict) -> dict:
        forecast_days = int(payload.get('forecast_days') or 14)
        forecast_days = max(1, min(forecast_days, 90))
        available_stock = int(payload.get('available_stock') or 0)
        locked_stock = int(payload.get('locked_stock') or 0)
        in_transit_stock = int(payload.get('in_transit_stock') or 0)
        safe_stock = int(payload.get('safe_stock') or 0)
        daily_sales = float(payload.get('daily_sales') or 0)
        selection_score = float(payload.get('selection_score') or 0)
        product_layer = payload.get('product_layer') or 'unknown'
        warning_level = payload.get('warning_level') or 'healthy'

        effective_stock = max(available_stock - locked_stock, 0)
        target_stock = ceil(daily_sales * forecast_days + safe_stock)
        stock_gap = target_stock - effective_stock - max(in_transit_stock, 0)
        suggest_quantity = max(0, stock_gap)
        reasons = []
        risks = []
        action = 'observe'

        if warning_level in ('critical', 'high') or effective_stock <= safe_stock:
            action = 'replenish'
            reasons.append('inventory_warning_triggered')
        if daily_sales <= 0:
            risks.append('insufficient_sales_history')
            suggest_quantity = max(0, safe_stock - effective_stock)
            action = 'observe' if suggest_quantity == 0 else 'small_batch_replenishment'
        if product_layer == 'risk' and selection_score < 0.25:
            risks.append('low_product_value_score')
            action = 'clearance_or_manual_review'
            suggest_quantity = 0
        elif product_layer == 'hot' and suggest_quantity > 0:
            reasons.append('hot_product_priority')
            suggest_quantity = ceil(suggest_quantity * 1.2)
        elif product_layer == 'long_tail' and suggest_quantity > 0:
            risks.append('long_tail_product')
            suggest_quantity = ceil(suggest_quantity * 0.6)

        if in_transit_stock > 0:
            reasons.append('in_transit_stock_considered')
        if suggest_quantity <= 0 and action == 'replenish':
            action = 'observe'

        return {
            'product_id': payload.get('product_id'),
            'forecast_days': forecast_days,
            'suggest_quantity': int(suggest_quantity),
            'target_stock': int(target_stock),
            'effective_stock': int(effective_stock),
            'daily_sales': round(daily_sales, 4),
            'action': action,
            'reason': reasons or ['stock_is_sufficient'],
            'risk_note': risks,
        }
