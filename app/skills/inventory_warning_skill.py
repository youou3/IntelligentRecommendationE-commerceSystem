from app.skills.base import BaseSkill


class InventoryWarningSkill(BaseSkill):
    name = 'inventory_warning'

    def validate(self, payload: dict) -> bool:
        return bool(payload.get('items'))

    def execute(self, payload: dict) -> dict:
        items = payload.get('items') or []
        warning_items = []

        for item in items:
            available_stock = int(item.get('available_stock') or 0)
            locked_stock = int(item.get('locked_stock') or 0)
            in_transit_stock = int(item.get('in_transit_stock') or 0)
            safe_stock = int(item.get('safe_stock') or 0)
            daily_sales = float(item.get('daily_sales') or 0)
            effective_stock = max(available_stock - locked_stock, 0)
            available_with_transit = effective_stock + max(in_transit_stock, 0)
            stockout_days = None
            if daily_sales > 0:
                stockout_days = round(available_with_transit / daily_sales, 2)

            reasons = []
            if effective_stock <= 0:
                level = 'critical'
                action = 'replenish_now'
                reasons.append('effective_stock_empty')
            elif effective_stock <= safe_stock:
                level = 'high'
                action = 'prepare_replenishment'
                reasons.append('below_safe_stock')
            elif stockout_days is not None and stockout_days <= 3:
                level = 'high'
                action = 'prepare_replenishment'
                reasons.append('stockout_within_3_days')
            elif stockout_days is not None and stockout_days <= 7:
                level = 'medium'
                action = 'observe'
                reasons.append('stockout_within_7_days')
            else:
                level = 'healthy'
                action = 'observe'

            if in_transit_stock > 0 and level in ('high', 'medium'):
                reasons.append('has_in_transit_stock')
            if item.get('product_status') not in (None, 'active'):
                reasons.append('product_not_active')
                if level == 'healthy':
                    level = 'medium'
                    action = 'check_product_status'

            warning_items.append({
                'product_id': item.get('product_id'),
                'warning_level': level,
                'warning_reason': reasons,
                'suggested_action': action,
                'effective_stock': effective_stock,
                'available_with_transit': available_with_transit,
                'forecast_daily_sales': round(daily_sales, 4),
                'stockout_days': stockout_days,
                'safe_stock': safe_stock,
            })

        level_rank = {'critical': 0, 'high': 1, 'medium': 2, 'healthy': 3}
        warning_items.sort(key=lambda row: (level_rank.get(row['warning_level'], 9), row['stockout_days'] if row['stockout_days'] is not None else 9999))
        return {'items': warning_items}
