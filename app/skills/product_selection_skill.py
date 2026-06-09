from app.skills.base import BaseSkill


def _clamp(value, low=0.0, high=1.0):
    return max(low, min(float(value), high))


class ProductSelectionSkill(BaseSkill):
    name = 'product_selection'

    def validate(self, payload: dict) -> bool:
        return bool(payload.get('products'))

    def execute(self, payload: dict) -> dict:
        products = payload.get('products') or []
        ranked = []

        for product in products:
            metrics = product.get('metrics') or {}
            exposure_count = float(metrics.get('exposure_count') or 0)
            click_count = float(metrics.get('click_count') or 0)
            add_cart_count = float(metrics.get('add_cart_count') or 0)
            convert_count = float(metrics.get('convert_count') or 0)
            ctr = click_count / max(exposure_count, 1.0)
            cart_rate = add_cart_count / max(exposure_count, 1.0)
            conversion_rate = convert_count / max(exposure_count, 1.0)
            gross_margin = _clamp(product.get('gross_margin', 0.0))
            effective_stock = float(product.get('effective_stock') or 0)
            inventory_score = min(effective_stock / 100.0, 1.0)
            conversion_score = min(conversion_rate / 0.10, 1.0)
            cart_score = min(cart_rate / 0.20, 1.0)
            ctr_score = min(ctr / 0.30, 1.0)
            selection_score = round(
                0.30 * conversion_score
                + 0.25 * cart_score
                + 0.20 * ctr_score
                + 0.15 * gross_margin
                + 0.10 * inventory_score,
                4,
            )

            if effective_stock <= 0 or product.get('status') != 'active' or selection_score < 0.25:
                layer = 'risk'
                advice = ['restock_or_hide', 'stop_recommendation_until_stock_recovers'] if effective_stock <= 0 else ['check_product_status']
            elif selection_score >= 0.50 and conversion_rate >= 0.03 and (ctr >= 0.20 or metrics.get('add_cart_count', 0) >= 10) and effective_stock > 0:
                layer = 'hot'
                advice = ['increase_exposure', 'maintain_inventory']
            elif selection_score >= 0.40 and ctr >= 0.10 and conversion_rate >= 0.02:
                layer = 'potential'
                advice = ['optimize_detail_page', 'consider_promotion']
                if effective_stock <= float(product.get('safe_stock') or 0):
                    advice.append('prepare_replenishment')
            else:
                layer = 'long_tail'
                advice = ['test_small_traffic'] if gross_margin >= 0.4 else ['reduce_exposure', 'consider_clearance']

            if not product.get('has_feedback'):
                advice = list(dict.fromkeys(advice))

            ranked.append({
                'product': product,
                'selection_score': selection_score,
                'layer': layer,
                'metrics': {
                    'exposure_count': int(exposure_count),
                    'click_count': int(click_count),
                    'add_cart_count': int(add_cart_count),
                    'convert_count': int(convert_count),
                    'ctr': round(ctr, 4),
                    'cart_rate': round(cart_rate, 4),
                    'conversion_rate': round(conversion_rate, 4),
                    'gross_margin': round(gross_margin, 4),
                    'effective_stock': int(effective_stock),
                },
                'advice': advice,
            })

        ranked.sort(key=lambda item: (item['selection_score'], item['metrics']['convert_count'], item['metrics']['click_count']), reverse=True)
        return {'items': ranked}
