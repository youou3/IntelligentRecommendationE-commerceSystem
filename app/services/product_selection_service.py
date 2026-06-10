from app.core.mcp import mcp_dispatcher
from app.core.database import db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_selection import ProductSelectionSnapshot
from app.models.recommendation_feedback import RecommendationFeedback


class ProductSelectionService:
    def select_scores(self, tenant_id: str, merchant_id: str, request_id: str, product_ids=None, date_range=None, persist: bool = True):
        query = Product.query.filter_by(tenant_id=tenant_id, merchant_id=merchant_id)
        if product_ids:
            query = query.filter(Product.id.in_(product_ids))
        products = query.all()
        product_map = {product.id: product for product in products}
        if not products:
            return {'items': []}

        inventory_rows = Inventory.query.filter(
            Inventory.tenant_id == tenant_id,
            Inventory.merchant_id == merchant_id,
            Inventory.product_id.in_(list(product_map.keys())),
        ).all()
        inventory_map = {row.product_id: row for row in inventory_rows}

        feedback_query = RecommendationFeedback.query.filter(
            RecommendationFeedback.tenant_id == tenant_id,
            RecommendationFeedback.merchant_id == merchant_id,
            RecommendationFeedback.product_id.in_(list(product_map.keys())),
        )
        if date_range and date_range.get('start'):
            from datetime import datetime
            start = datetime.fromisoformat(date_range['start'])
            feedback_query = feedback_query.filter(RecommendationFeedback.created_at >= start)
        if date_range and date_range.get('end'):
            from datetime import datetime, timedelta
            end = datetime.fromisoformat(date_range['end']) + timedelta(days=1)
            feedback_query = feedback_query.filter(RecommendationFeedback.created_at < end)
        feedback_rows = feedback_query.all()
        feedback_map = {}
        for row in feedback_rows:
            stat = feedback_map.setdefault(row.product_id, {'exposure': 0, 'click': 0, 'add_cart': 0, 'convert': 0})
            stat[row.feedback_type] += 1

        payload_products = []
        for product in products:
            inventory = inventory_map.get(product.id)
            effective_stock = (inventory.available_stock - inventory.locked_stock) if inventory else 0
            feedback_stat = feedback_map.get(product.id, {'exposure': 0, 'click': 0, 'add_cart': 0, 'convert': 0})
            payload_products.append({
                'product_id': product.id,
                'name': product.name,
                'category_id': product.category_id,
                'tags': product.tags or [],
                'gross_margin': float(product.gross_margin or 0),
                'status': product.status,
                'effective_stock': effective_stock,
                'safe_stock': inventory.safe_stock if inventory else 0,
                'metrics': {
                    'exposure_count': feedback_stat['exposure'],
                    'click_count': feedback_stat['click'],
                    'add_cart_count': feedback_stat['add_cart'],
                    'convert_count': feedback_stat['convert'],
                },
                'has_feedback': sum(feedback_stat.values()) > 0,
            })

        ranked_response = mcp_dispatcher.call(
            'product_selection',
            {'products': payload_products},
            tenant_id=tenant_id,
            merchant_id=merchant_id,
            request_id=request_id,
            fallback_payload={'items': []},
        )
        ranked = ranked_response['data']['items']

        if persist:
            for item in ranked:
                product = product_map[item['product']['product_id']]
                product.selection_score = item['selection_score']
                product.product_layer = item['layer']
                product.operation_advice = item['advice']
                db.session.add(ProductSelectionSnapshot(
                    tenant_id=tenant_id,
                    merchant_id=merchant_id,
                    request_id=request_id,
                    product_id=product.id,
                    selection_score=item['selection_score'],
                    layer=item['layer'],
                    metrics=item['metrics'],
                    advice=item['advice'],
                ))
            db.session.commit()

        return {
            'items': [
                {
                    'product_id': item['product']['product_id'],
                    'name': item['product']['name'],
                    'selection_score': item['selection_score'],
                    'layer': item['layer'],
                    'metrics': item['metrics'],
                    'advice': item['advice'],
                }
                for item in ranked
            ]
        }
