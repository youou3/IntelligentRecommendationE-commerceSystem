from datetime import datetime, timedelta
from uuid import uuid4

from app.core.database import db, get_mongo_db
from app.models.inventory import Inventory, InventoryLog, InventoryWarning, ReplenishmentOrder
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.services.product_selection_service import ProductSelectionService
from app.skills.inventory_warning_skill import InventoryWarningSkill
from app.skills.replenishment_skill import ReplenishmentSkill


class InventoryService:
    warning_skill = InventoryWarningSkill()
    replenishment_skill = ReplenishmentSkill()

    def __init__(self):
        self.product_selection_service = ProductSelectionService()

    def _record_workflow_run(self, tenant_id, merchant_id, workflow_name, request_id, status, input_payload, output_payload=None, error_message=None, run_id=None):
        mongo_db = get_mongo_db()
        run_id = run_id or f'RUN-{uuid4().hex[:12]}'
        if mongo_db is not None:
            now = datetime.utcnow()
            mongo_db.workflow_runs.insert_one({
                'tenant_id': tenant_id,
                'merchant_id': merchant_id,
                'workflow_name': workflow_name,
                'run_id': run_id,
                'request_id': request_id,
                'status': status,
                'input_payload': input_payload,
                'output_payload': output_payload or {},
                'error_message': error_message,
                'started_at': now,
                'finished_at': now,
                'created_at': now,
            })
        return run_id

    def _sales_map(self, tenant_id, merchant_id, product_ids, days):
        if not product_ids:
            return {}
        start_at = datetime.utcnow() - timedelta(days=days)
        rows = db.session.query(
            OrderItem.product_id,
            db.func.coalesce(db.func.sum(OrderItem.quantity), 0),
        ).join(
            Order,
            db.and_(
                Order.id == OrderItem.order_id,
                Order.tenant_id == OrderItem.tenant_id,
                Order.merchant_id == OrderItem.merchant_id,
            ),
        ).filter(
            OrderItem.tenant_id == tenant_id,
            OrderItem.merchant_id == merchant_id,
            OrderItem.product_id.in_(product_ids),
            Order.created_at >= start_at,
            Order.pay_status == 'paid',
            Order.order_status.in_(('paid', 'completed', 'shipped')),
        ).group_by(OrderItem.product_id).all()
        return {product_id: int(quantity or 0) for product_id, quantity in rows}

    def _warning_payload_items(self, tenant_id, merchant_id, product_ids=None, sales_days=7):
        query = Inventory.query.filter_by(tenant_id=tenant_id, merchant_id=merchant_id)
        if product_ids:
            query = query.filter(Inventory.product_id.in_(product_ids))
        inventory_rows = query.all()
        product_ids = [row.product_id for row in inventory_rows]
        products = Product.query.filter(
            Product.tenant_id == tenant_id,
            Product.merchant_id == merchant_id,
            Product.id.in_(product_ids),
        ).all() if product_ids else []
        product_map = {product.id: product for product in products}
        sales_map = self._sales_map(tenant_id, merchant_id, product_ids, sales_days)

        items = []
        for row in inventory_rows:
            product = product_map.get(row.product_id)
            quantity = sales_map.get(row.product_id, 0)
            items.append({
                'product_id': row.product_id,
                'available_stock': row.available_stock,
                'locked_stock': row.locked_stock,
                'in_transit_stock': row.in_transit_stock,
                'safe_stock': row.safe_stock,
                'daily_sales': quantity / max(sales_days, 1),
                'product_status': product.status if product else None,
            })
        return items

    def run_warning_workflow(self, tenant_id, merchant_id, request_id, product_ids=None, sales_days=7, persist=True):
        input_payload = {
            'product_ids': product_ids,
            'sales_days': sales_days,
            'persist': persist,
        }
        payload_items = self._warning_payload_items(tenant_id, merchant_id, product_ids, sales_days)
        skill_result = self.warning_skill.execute({'items': payload_items})
        items = skill_result['items']

        if persist:
            mongo_db = get_mongo_db()
            now = datetime.utcnow()
            for item in items:
                if item['warning_level'] == 'healthy':
                    continue
                warning = InventoryWarning(
                    tenant_id=tenant_id,
                    merchant_id=merchant_id,
                    product_id=item['product_id'],
                    warning_level=item['warning_level'],
                    warning_reason=item['warning_reason'],
                    status='triggered',
                    request_id=request_id,
                    forecast_daily_sales=item['forecast_daily_sales'],
                    stockout_days=item['stockout_days'],
                    suggested_action=item['suggested_action'],
                )
                db.session.add(warning)
                if mongo_db is not None:
                    mongo_db.inventory_warning_logs.insert_one({
                        'tenant_id': tenant_id,
                        'merchant_id': merchant_id,
                        'request_id': request_id,
                        'product_id': item['product_id'],
                        'warning_level': item['warning_level'],
                        'warning_reason': item['warning_reason'],
                        'status': 'triggered',
                        'created_at': now,
                    })
            db.session.commit()

        run_id = self._record_workflow_run(
            tenant_id,
            merchant_id,
            'inventory_warning',
            request_id,
            'success',
            input_payload,
            {'items': items},
        )
        return {'run_id': run_id, 'items': items}

    def list_warnings(self, tenant_id, merchant_id, warning_level=None, category_id=None, status=None, page=1, page_size=20, request_id=None):
        query = InventoryWarning.query.filter_by(tenant_id=tenant_id, merchant_id=merchant_id)
        if warning_level:
            query = query.filter(InventoryWarning.warning_level == warning_level)
        if status:
            query = query.filter(InventoryWarning.status == status)
        if category_id:
            query = query.join(Product, db.and_(
                Product.id == InventoryWarning.product_id,
                Product.tenant_id == InventoryWarning.tenant_id,
                Product.merchant_id == InventoryWarning.merchant_id,
            )).filter(Product.category_id == category_id)

        total = query.count()
        rows = query.order_by(InventoryWarning.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        product_map = {}
        product_ids = [row.product_id for row in rows]
        if product_ids:
            products = Product.query.filter(
                Product.tenant_id == tenant_id,
                Product.merchant_id == merchant_id,
                Product.id.in_(product_ids),
            ).all()
            product_map = {product.id: product for product in products}

        return {
            'request_id': request_id,
            'page': page,
            'page_size': page_size,
            'total': total,
            'items': [
                {
                    'id': row.id,
                    'product_id': row.product_id,
                    'product_name': product_map.get(row.product_id).name if product_map.get(row.product_id) else None,
                    'category_id': product_map.get(row.product_id).category_id if product_map.get(row.product_id) else None,
                    'warning_level': row.warning_level,
                    'warning_reason': row.warning_reason,
                    'status': row.status,
                    'forecast_daily_sales': float(row.forecast_daily_sales or 0),
                    'stockout_days': float(row.stockout_days) if row.stockout_days is not None else None,
                    'suggested_action': row.suggested_action,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                }
                for row in rows
            ],
        }

    def suggest_replenishment(self, tenant_id, merchant_id, request_id, product_id, forecast_days=14, warning_id=None, persist=True):
        inventory = Inventory.query.filter_by(tenant_id=tenant_id, merchant_id=merchant_id, product_id=product_id).first()
        if inventory is None:
            raise ValueError('inventory not found')

        sales_days = min(max(int(forecast_days), 1), 90)
        quantity = self._sales_map(tenant_id, merchant_id, [product_id], sales_days).get(product_id, 0)
        product = Product.query.filter_by(tenant_id=tenant_id, merchant_id=merchant_id, id=product_id).first()
        warning = None
        if warning_id:
            warning = InventoryWarning.query.filter_by(tenant_id=tenant_id, merchant_id=merchant_id, id=warning_id).first()
        if warning is None:
            warning = InventoryWarning.query.filter_by(
                tenant_id=tenant_id,
                merchant_id=merchant_id,
                product_id=product_id,
                status='triggered',
            ).order_by(InventoryWarning.created_at.desc()).first()

        selection = self.product_selection_service.select_scores(
            tenant_id=tenant_id,
            merchant_id=merchant_id,
            request_id=request_id,
            product_ids=[product_id],
            persist=False,
        )
        selection_item = selection['items'][0] if selection['items'] else {}
        computed_score = float(selection_item.get('selection_score') or 0)
        persisted_score = float(product.selection_score or 0) if product else 0
        selection_score = max(computed_score, persisted_score)
        product_layer = selection_item.get('layer')
        if persisted_score >= computed_score and product and product.product_layer:
            product_layer = product.product_layer
        payload = {
            'product_id': product_id,
            'forecast_days': forecast_days,
            'available_stock': inventory.available_stock,
            'locked_stock': inventory.locked_stock,
            'in_transit_stock': inventory.in_transit_stock,
            'safe_stock': inventory.safe_stock,
            'daily_sales': quantity / max(sales_days, 1),
            'selection_score': selection_score,
            'product_layer': product_layer or (product.product_layer if product else None),
            'warning_level': warning.warning_level if warning else 'healthy',
        }
        result = self.replenishment_skill.execute(payload)
        status = 'pending_approval' if result['suggest_quantity'] > 0 and result['action'] in ('replenish', 'small_batch_replenishment') else 'draft'

        order_id = None
        if persist:
            existing = ReplenishmentOrder.query.filter_by(
                tenant_id=tenant_id,
                merchant_id=merchant_id,
                request_id=request_id,
                product_id=product_id,
            ).first()
            if existing:
                order = existing
                order.suggest_quantity = result['suggest_quantity']
                order.status = status
                order.forecast_days = result['forecast_days']
                order.reason = result['reason']
                order.risk_note = result['risk_note']
                order.source_warning_id = warning.id if warning else None
            else:
                order = ReplenishmentOrder(
                    tenant_id=tenant_id,
                    merchant_id=merchant_id,
                    product_id=product_id,
                    suggest_quantity=result['suggest_quantity'],
                    status=status,
                    request_id=request_id,
                    forecast_days=result['forecast_days'],
                    reason=result['reason'],
                    risk_note=result['risk_note'],
                    source_warning_id=warning.id if warning else None,
                )
                db.session.add(order)
            db.session.commit()
            order_id = order.id

        run_id = self._record_workflow_run(
            tenant_id,
            merchant_id,
            'auto_replenishment',
            request_id,
            'success',
            {'product_id': product_id, 'forecast_days': forecast_days, 'warning_id': warning_id, 'persist': persist},
            {'result': result, 'replenishment_order_id': order_id, 'status': status},
        )
        return {
            **result,
            'run_id': run_id,
            'replenishment_order_id': order_id,
            'status': status,
            'selection_score': payload['selection_score'],
            'product_layer': payload['product_layer'],
            'warning_level': payload['warning_level'],
        }

    def apply_inventory_event(self, tenant_id, merchant_id, request_id, event_id, product_id, change_type, quantity):
        existing = InventoryLog.query.filter_by(tenant_id=tenant_id, merchant_id=merchant_id, event_id=event_id).first()
        if existing:
            return {'idempotent': True, 'inventory_log_id': existing.id, 'product_id': product_id}

        inventory = Inventory.query.filter_by(tenant_id=tenant_id, merchant_id=merchant_id, product_id=product_id).first()
        if inventory is None:
            inventory = Inventory(tenant_id=tenant_id, merchant_id=merchant_id, product_id=product_id)
            db.session.add(inventory)
            db.session.flush()

        quantity = int(quantity)
        before = self._inventory_snapshot(inventory)
        if change_type in ('purchase_paid', 'stock_out'):
            inventory.available_stock = max(inventory.available_stock - quantity, 0)
        elif change_type in ('refund', 'cancel_order', 'stock_in'):
            inventory.available_stock += quantity
        elif change_type == 'lock':
            inventory.locked_stock += quantity
        elif change_type == 'release_lock':
            inventory.locked_stock = max(inventory.locked_stock - quantity, 0)
        elif change_type == 'in_transit':
            inventory.in_transit_stock += quantity
        elif change_type == 'receive_transit':
            inventory.in_transit_stock = max(inventory.in_transit_stock - quantity, 0)
            inventory.available_stock += quantity
        else:
            raise ValueError('unsupported inventory change_type')

        after = self._inventory_snapshot(inventory)
        log = InventoryLog(
            tenant_id=tenant_id,
            merchant_id=merchant_id,
            product_id=product_id,
            change_type=change_type,
            change_quantity=quantity,
            request_id=request_id,
            event_id=event_id,
            before_snapshot=before,
            after_snapshot=after,
        )
        db.session.add(log)
        db.session.commit()
        return {'idempotent': False, 'inventory_log_id': log.id, 'product_id': product_id, 'inventory': after}

    def _inventory_snapshot(self, inventory):
        return {
            'available_stock': inventory.available_stock,
            'locked_stock': inventory.locked_stock,
            'in_transit_stock': inventory.in_transit_stock,
            'safe_stock': inventory.safe_stock,
        }
