from collections import Counter, defaultdict
from datetime import datetime, timedelta

from app.core.database import db, get_mongo_db
from app.models.inventory import Inventory, InventoryWarning, ReplenishmentOrder
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.product_selection import ProductSelectionSnapshot
from app.models.recommendation_feedback import RecommendationFeedback
from app.models.user_profile import UserProfile


class DashboardService:
    def _parse_date(self, value):
        if not value:
            return None
        return datetime.fromisoformat(value)

    def _parse_filters(self, args):
        start_date = args.get('start_date')
        end_date = args.get('end_date')
        if not start_date and not end_date:
            end_date_dt = datetime.utcnow()
            start_date_dt = end_date_dt - timedelta(days=6)
        elif start_date and not end_date:
            start_date_dt = self._parse_date(start_date)
            end_date_dt = datetime.utcnow()
        elif end_date and not start_date:
            end_date_dt = self._parse_date(end_date)
            start_date_dt = end_date_dt - timedelta(days=6)
        else:
            start_date_dt = self._parse_date(start_date)
            end_date_dt = self._parse_date(end_date)
        if start_date_dt is None or end_date_dt is None:
            raise ValueError('invalid date format')
        if start_date_dt.tzinfo is not None:
            start_date_dt = start_date_dt.replace(tzinfo=None)
        if end_date_dt.tzinfo is not None:
            end_date_dt = end_date_dt.replace(tzinfo=None)
        end_exclusive_dt = end_date_dt + timedelta(days=1)
        return {
            'tenant_id': args.get('tenant_id'),
            'merchant_id': args.get('merchant_id'),
            'request_id': args.get('request_id'),
            'scene': args.get('scene'),
            'category_id': args.get('category_id'),
            'limit': max(1, min(int(args.get('limit', 10)), 100)),
            'start_date': start_date_dt,
            'end_date': end_date_dt,
            'end_exclusive_dt': end_exclusive_dt,
        }

    def _safe_rate(self, numerator, denominator):
        denominator = denominator or 0
        if denominator == 0:
            return 0
        return round(float(numerator) / float(denominator), 4)

    def _mongo_logs(self, filters):
        mongo_db = get_mongo_db()
        if mongo_db is None:
            return {'behavior_events': [], 'recommendation_logs': []}
        mongo_query = {
            'tenant_id': filters['tenant_id'],
            'merchant_id': filters['merchant_id'],
            'created_at': {'$gte': filters['start_date'], '$lt': filters['end_exclusive_dt']},
        }
        if filters.get('scene'):
            mongo_query['scene'] = filters['scene']
        behavior_events = list(mongo_db.behavior_events.find(mongo_query))
        recommendation_logs = list(mongo_db.recommendation_logs.find(mongo_query))
        return {
            'behavior_events': behavior_events,
            'recommendation_logs': recommendation_logs,
        }

    def _feedback_rows(self, filters):
        query = RecommendationFeedback.query.filter(
            RecommendationFeedback.tenant_id == filters['tenant_id'],
            RecommendationFeedback.merchant_id == filters['merchant_id'],
            RecommendationFeedback.created_at >= filters['start_date'],
            RecommendationFeedback.created_at < filters['end_exclusive_dt'],
        )
        if filters.get('scene'):
            query = query.filter(RecommendationFeedback.scene == filters['scene'])
        return query.all()

    def _inventory_map(self, filters):
        rows = Inventory.query.filter_by(
            tenant_id=filters['tenant_id'],
            merchant_id=filters['merchant_id'],
        ).all()
        return {row.product_id: row for row in rows}

    def _product_map(self, filters):
        rows = Product.query.filter_by(
            tenant_id=filters['tenant_id'],
            merchant_id=filters['merchant_id'],
        ).all()
        return {row.id: row for row in rows}

    def _profile_rows(self, filters):
        rows = UserProfile.query.filter_by(
            tenant_id=filters['tenant_id'],
            merchant_id=filters['merchant_id'],
        ).all()
        return rows

    def _workflow_rows(self, filters):
        mongo_db = get_mongo_db()
        if mongo_db is None:
            return []
        query = {
            'tenant_id': filters['tenant_id'],
            'merchant_id': filters['merchant_id'],
            'created_at': {'$gte': filters['start_date'], '$lt': filters['end_exclusive_dt']},
        }
        return list(mongo_db.workflow_runs.find(query).sort('created_at', -1).limit(filters['limit']))

    def _skill_call_rows(self, filters):
        mongo_db = get_mongo_db()
        if mongo_db is None:
            return []
        query = {
            'tenant_id': filters['tenant_id'],
            'merchant_id': filters['merchant_id'],
            'created_at': {'$gte': filters['start_date'], '$lt': filters['end_exclusive_dt']},
        }
        return list(mongo_db.skill_call_logs.find(query).sort('created_at', -1).limit(200))

    def _paid_sales_by_product(self, filters, product_ids=None):
        query = db.session.query(
            OrderItem.product_id,
            db.func.coalesce(db.func.sum(OrderItem.quantity), 0),
            db.func.coalesce(db.func.sum(OrderItem.amount), 0),
        ).join(
            Order,
            db.and_(
                Order.id == OrderItem.order_id,
                Order.tenant_id == OrderItem.tenant_id,
                Order.merchant_id == OrderItem.merchant_id,
            ),
        ).filter(
            OrderItem.tenant_id == filters['tenant_id'],
            OrderItem.merchant_id == filters['merchant_id'],
            Order.created_at >= filters['start_date'],
            Order.created_at < filters['end_exclusive_dt'],
            Order.pay_status == 'paid',
            Order.order_status.in_(('paid', 'completed', 'shipped')),
        )
        if product_ids:
            query = query.filter(OrderItem.product_id.in_(product_ids))
        rows = query.group_by(OrderItem.product_id).all()
        return {
            product_id: {
                'sold_quantity': int(quantity or 0),
                'sales_amount': float(amount or 0),
            }
            for product_id, quantity, amount in rows
        }

    def get_overview(self, filters):
        mongo_data = self._mongo_logs(filters)
        feedback_rows = self._feedback_rows(filters)
        products = self._product_map(filters)
        inventory_map = self._inventory_map(filters)
        profiles = self._profile_rows(filters)

        exposures = sum(1 for row in feedback_rows if row.feedback_type == 'exposure')
        clicks = sum(1 for row in feedback_rows if row.feedback_type == 'click')
        add_carts = sum(1 for row in feedback_rows if row.feedback_type == 'add_cart')
        conversions = sum(1 for row in feedback_rows if row.feedback_type == 'convert')
        low_stock_products = 0
        for product_id, product in products.items():
            inventory = inventory_map.get(product_id)
            effective_stock = (inventory.available_stock - inventory.locked_stock) if inventory else 0
            safe_stock = inventory.safe_stock if inventory else 0
            if effective_stock <= safe_stock:
                low_stock_products += 1

        return {
            'filters': {
                'tenant_id': filters['tenant_id'],
                'merchant_id': filters['merchant_id'],
                'start_date': filters['start_date'].date().isoformat(),
                'end_date': filters['end_date'].date().isoformat(),
                'scene': filters.get('scene'),
            },
            'kpis': {
                'behavior_events': len(mongo_data['behavior_events']),
                'recommendation_requests': len(mongo_data['recommendation_logs']),
                'exposures': exposures,
                'clicks': clicks,
                'add_carts': add_carts,
                'conversions': conversions,
                'ctr': self._safe_rate(clicks, exposures),
                'add_cart_rate': self._safe_rate(add_carts, exposures),
                'conversion_rate': self._safe_rate(conversions, exposures),
                'active_products': sum(1 for product in products.values() if product.status == 'active'),
                'low_stock_products': low_stock_products,
                'profiled_users': len(profiles),
            },
        }

    def get_recommendation_funnel(self, filters):
        mongo_data = self._mongo_logs(filters)
        feedback_rows = self._feedback_rows(filters)
        daily = defaultdict(lambda: {'recommendation_requests': 0, 'exposures': 0, 'clicks': 0, 'add_carts': 0, 'conversions': 0})

        for log in mongo_data['recommendation_logs']:
            date_key = log['created_at'].date().isoformat()
            daily[date_key]['recommendation_requests'] += 1

        for row in feedback_rows:
            date_key = row.created_at.date().isoformat()
            daily[date_key][f"{row.feedback_type}s" if row.feedback_type != 'convert' else 'conversions'] += 1

        trend = []
        current = filters['start_date'].date()
        end_date = filters['end_date'].date()
        while current <= end_date:
            key = current.isoformat()
            row = daily[key]
            trend.append({
                'date': key,
                'recommendation_requests': row['recommendation_requests'],
                'exposures': row['exposures'],
                'clicks': row['clicks'],
                'add_carts': row['add_carts'],
                'conversions': row['conversions'],
            })
            current += timedelta(days=1)

        summary = {
            'recommendation_requests': len(mongo_data['recommendation_logs']),
            'exposures': sum(1 for row in feedback_rows if row.feedback_type == 'exposure'),
            'clicks': sum(1 for row in feedback_rows if row.feedback_type == 'click'),
            'add_carts': sum(1 for row in feedback_rows if row.feedback_type == 'add_cart'),
            'conversions': sum(1 for row in feedback_rows if row.feedback_type == 'convert'),
        }
        summary['ctr'] = self._safe_rate(summary['clicks'], summary['exposures'])
        summary['add_cart_rate'] = self._safe_rate(summary['add_carts'], summary['exposures'])
        summary['conversion_rate'] = self._safe_rate(summary['conversions'], summary['exposures'])

        by_scene = defaultdict(lambda: {'exposures': 0, 'clicks': 0, 'add_carts': 0, 'conversions': 0})
        for row in feedback_rows:
            scene = row.scene or 'default'
            if row.feedback_type == 'exposure':
                by_scene[scene]['exposures'] += 1
            elif row.feedback_type == 'click':
                by_scene[scene]['clicks'] += 1
            elif row.feedback_type == 'add_cart':
                by_scene[scene]['add_carts'] += 1
            elif row.feedback_type == 'convert':
                by_scene[scene]['conversions'] += 1

        scene_rows = []
        for scene, row in by_scene.items():
            scene_rows.append({
                'scene': scene,
                'exposures': row['exposures'],
                'clicks': row['clicks'],
                'add_carts': row['add_carts'],
                'conversions': row['conversions'],
                'ctr': self._safe_rate(row['clicks'], row['exposures']),
                'conversion_rate': self._safe_rate(row['conversions'], row['exposures']),
            })

        return {
            'summary': summary,
            'funnel': [
                {'stage': 'exposure', 'label': '曝光', 'count': summary['exposures'], 'rate_from_previous': 1.0},
                {'stage': 'click', 'label': '点击', 'count': summary['clicks'], 'rate_from_previous': self._safe_rate(summary['clicks'], summary['exposures'])},
                {'stage': 'add_cart', 'label': '加购', 'count': summary['add_carts'], 'rate_from_previous': self._safe_rate(summary['add_carts'], summary['clicks'])},
                {'stage': 'convert', 'label': '转化', 'count': summary['conversions'], 'rate_from_previous': self._safe_rate(summary['conversions'], summary['add_carts'])},
            ],
            'trend': trend,
            'by_scene': scene_rows,
        }

    def get_product_selection(self, filters):
        products = self._product_map(filters)
        inventory_map = self._inventory_map(filters)
        feedback_rows = self._feedback_rows(filters)
        counts = defaultdict(lambda: {'exposure': 0, 'click': 0, 'add_cart': 0, 'convert': 0})
        for row in feedback_rows:
            counts[row.product_id][row.feedback_type] += 1

        layer_distribution = Counter()
        top_products = []
        risk_products = []
        for product_id, product in products.items():
            inventory = inventory_map.get(product_id)
            effective_stock = (inventory.available_stock - inventory.locked_stock) if inventory else 0
            safe_stock = inventory.safe_stock if inventory else 0
            stat = counts[product_id]
            layer = product.product_layer or 'unknown'
            layer_distribution[layer] += 1
            ctr = self._safe_rate(stat['click'], stat['exposure'])
            conversion_rate = self._safe_rate(stat['convert'], stat['exposure'])
            item = {
                'product_id': product_id,
                'name': product.name,
                'category_id': product.category_id,
                'selection_score': float(product.selection_score or 0),
                'layer': layer,
                'effective_stock': effective_stock,
                'safe_stock': safe_stock,
                'exposures': stat['exposure'],
                'clicks': stat['click'],
                'add_carts': stat['add_cart'],
                'conversions': stat['convert'],
                'ctr': ctr,
                'conversion_rate': conversion_rate,
            }
            if product.product_layer in ('hot', 'potential') or product.selection_score:
                top_products.append(item)
            if effective_stock <= 0 or product.status != 'active' or float(product.selection_score or 0) < 0.25:
                item['risk_type'] = 'low_stock' if effective_stock <= 0 else 'status_or_score'
                risk_products.append(item)

        top_products.sort(key=lambda x: x['selection_score'], reverse=True)
        layer_rows = [{'layer': layer, 'count': count} for layer, count in layer_distribution.items()]

        return {
            'layer_distribution': layer_rows,
            'top_products': top_products[:filters['limit']],
            'risk_products': risk_products[:filters['limit']],
        }

    def get_user_profiles(self, filters):
        profiles = self._profile_rows(filters)
        mongo_data = self._mongo_logs(filters)
        active_behavior_users = {row.get('user_id') for row in mongo_data['behavior_events'] if row.get('user_id')}

        stage_counter = Counter()
        category_counter = Counter()
        tag_counter = Counter()
        price_bucket_counter = Counter()
        total_tagged = 0
        for profile in profiles:
            stage_counter[profile.user_stage or 'unknown'] += 1
            if profile.category_preference:
                for category_id, weight in profile.category_preference.items():
                    category_counter[category_id] += float(weight or 0)
            if profile.tag_vector:
                for tag, weight in profile.tag_vector.items():
                    tag_counter[tag] += float(weight or 0)
                    total_tagged += 1
            if profile.price_preference:
                avg_price = profile.price_preference.get('avg')
                if avg_price is not None:
                    if avg_price < 100:
                        price_bucket_counter['low'] += 1
                    elif avg_price < 300:
                        price_bucket_counter['middle'] += 1
                    else:
                        price_bucket_counter['high'] += 1

        return {
            'summary': {
                'profiled_users': len(profiles),
                'active_behavior_users': len(active_behavior_users),
                'profile_coverage': self._safe_rate(len(profiles), len(active_behavior_users) or len(profiles) or 1),
            },
            'stage_distribution': [{'user_stage': stage, 'count': count} for stage, count in stage_counter.items()],
            'top_categories': [{'category_id': category_id, 'weight': round(weight, 4), 'user_count': 1} for category_id, weight in category_counter.most_common(filters['limit'])],
            'top_tags': [{'tag': tag, 'weight': round(weight, 4), 'user_count': 1} for tag, weight in tag_counter.most_common(filters['limit'])],
            'price_preference': [{'bucket': bucket, 'count': count} for bucket, count in price_bucket_counter.items()],
        }

    def get_inventory_health(self, filters):
        products = self._product_map(filters)
        inventory_map = self._inventory_map(filters)
        category_counter = defaultdict(lambda: {'product_count': 0, 'effective_stock': 0, 'low_stock_products': 0, 'out_of_stock_products': 0})
        risk_products = []
        active_products = 0
        inactive_products = 0
        low_stock_products = 0
        out_of_stock_products = 0

        for product_id, product in products.items():
            inventory = inventory_map.get(product_id)
            available_stock = inventory.available_stock if inventory else 0
            locked_stock = inventory.locked_stock if inventory else 0
            safe_stock = inventory.safe_stock if inventory else 0
            effective_stock = available_stock - locked_stock
            category_id = product.category_id or 'unknown'
            category_counter[category_id]['product_count'] += 1
            category_counter[category_id]['effective_stock'] += effective_stock
            if product.status == 'active':
                active_products += 1
            else:
                inactive_products += 1
            if effective_stock <= 0:
                out_of_stock_products += 1
                category_counter[category_id]['out_of_stock_products'] += 1
                risk_level = 'out_of_stock'
            elif effective_stock <= safe_stock:
                low_stock_products += 1
                category_counter[category_id]['low_stock_products'] += 1
                risk_level = 'low_stock'
            else:
                risk_level = 'healthy'
            if risk_level != 'healthy' or product.status != 'active':
                risk_products.append({
                    'product_id': product_id,
                    'name': product.name,
                    'category_id': category_id,
                    'status': product.status,
                    'available_stock': available_stock,
                    'locked_stock': locked_stock,
                    'effective_stock': effective_stock,
                    'safe_stock': safe_stock,
                    'risk_level': risk_level,
                })

        return {
            'summary': {
                'total_products': len(products),
                'active_products': active_products,
                'inactive_products': inactive_products,
                'low_stock_products': low_stock_products,
                'out_of_stock_products': out_of_stock_products,
                'healthy_products': len(products) - len(risk_products),
            },
            'stock_by_category': [
                {
                    'category_id': category_id,
                    'product_count': row['product_count'],
                    'effective_stock': row['effective_stock'],
                    'low_stock_products': row['low_stock_products'],
                    'out_of_stock_products': row['out_of_stock_products'],
                }
                for category_id, row in category_counter.items()
            ],
            'risk_products': risk_products[:filters['limit']],
        }

    def get_replenishment_review(self, filters):
        query = ReplenishmentOrder.query.filter(
            ReplenishmentOrder.tenant_id == filters['tenant_id'],
            ReplenishmentOrder.merchant_id == filters['merchant_id'],
            ReplenishmentOrder.created_at >= filters['start_date'],
            ReplenishmentOrder.created_at < filters['end_exclusive_dt'],
        )
        rows = query.order_by(ReplenishmentOrder.created_at.desc()).all()
        product_ids = [row.product_id for row in rows]
        product_map = self._product_map(filters)
        inventory_map = self._inventory_map(filters)
        sales_map = self._paid_sales_by_product(filters, product_ids)

        status_counter = Counter(row.status for row in rows)
        suggested_total = sum(int(row.suggest_quantity or 0) for row in rows)
        approved_total = sum(int(row.approved_quantity or 0) for row in rows if row.approved_quantity is not None)
        pending_approval = sum(1 for row in rows if row.status == 'pending_approval')
        received_orders = sum(1 for row in rows if row.status == 'received')
        closed_orders = sum(1 for row in rows if row.status == 'closed')

        items = []
        for row in rows:
            product = product_map.get(row.product_id)
            inventory = inventory_map.get(row.product_id)
            sales = sales_map.get(row.product_id, {'sold_quantity': 0, 'sales_amount': 0})
            effective_stock = (inventory.available_stock - inventory.locked_stock) if inventory else 0
            approved_quantity = row.approved_quantity if row.approved_quantity is not None else 0
            fulfill_rate = self._safe_rate(approved_quantity, row.suggest_quantity)
            sell_through_rate = self._safe_rate(sales['sold_quantity'], approved_quantity or row.suggest_quantity)
            items.append({
                'replenishment_order_id': row.id,
                'product_id': row.product_id,
                'product_name': product.name if product else None,
                'category_id': product.category_id if product else None,
                'suggest_quantity': row.suggest_quantity,
                'approved_quantity': row.approved_quantity,
                'status': row.status,
                'forecast_days': row.forecast_days,
                'reason': row.reason,
                'risk_note': row.risk_note,
                'effective_stock': effective_stock,
                'sold_quantity': sales['sold_quantity'],
                'sales_amount': sales['sales_amount'],
                'fulfill_rate': fulfill_rate,
                'sell_through_rate': sell_through_rate,
                'created_at': row.created_at.isoformat() if row.created_at else None,
            })

        items.sort(key=lambda item: (item['status'] in ('pending_approval', 'draft'), item['sell_through_rate'], item['suggest_quantity']), reverse=True)
        return {
            'summary': {
                'replenishment_orders': len(rows),
                'suggested_quantity': suggested_total,
                'approved_quantity': approved_total,
                'pending_approval': pending_approval,
                'received_orders': received_orders,
                'closed_orders': closed_orders,
                'approval_rate': self._safe_rate(sum(1 for row in rows if row.status in ('approved', 'purchasing', 'in_transit', 'received', 'closed')), len(rows)),
                'receive_rate': self._safe_rate(received_orders + closed_orders, len(rows)),
            },
            'status_distribution': [{'status': status, 'count': count} for status, count in status_counter.items()],
            'items': items[:filters['limit']],
        }

    def get_operations_review(self, filters):
        overview = self.get_overview(filters)
        funnel = self.get_recommendation_funnel(filters)
        selection = self.get_product_selection(filters)
        profiles = self.get_user_profiles(filters)
        inventory = self.get_inventory_health(filters)
        replenishment = self.get_replenishment_review(filters)
        workflows = self._workflow_rows(filters)
        skill_calls = self._skill_call_rows(filters)

        failed_skill_calls = sum(1 for row in skill_calls if row.get('status') == 'failed')
        fallback_skill_calls = sum(1 for row in skill_calls if row.get('fallback_used'))
        avg_cost_ms = round(sum(float(row.get('cost_ms') or 0) for row in skill_calls) / len(skill_calls), 2) if skill_calls else 0
        workflow_failed = sum(1 for row in workflows if row.get('status') in ('failed', 'error'))

        risk_products = selection['risk_products'][:filters['limit']]
        high_value_products = selection['top_products'][:filters['limit']]
        low_stock_products = inventory['risk_products'][:filters['limit']]
        strong_intent_users = [
            row for row in profiles['stage_distribution']
            if row.get('user_stage') in ('strong_intent', 'converted')
        ]

        return {
            'summary': {
                'tenant_id': filters['tenant_id'],
                'merchant_id': filters['merchant_id'],
                'start_date': filters['start_date'].date().isoformat(),
                'end_date': filters['end_date'].date().isoformat(),
                'recommendation_conversion_rate': funnel['summary']['conversion_rate'],
                'profile_coverage': profiles['summary']['profile_coverage'],
                'risk_products': len(risk_products),
                'low_stock_products': inventory['summary']['low_stock_products'],
                'replenishment_orders': replenishment['summary']['replenishment_orders'],
                'skill_calls': len(skill_calls),
                'skill_failed_calls': failed_skill_calls,
                'skill_fallback_calls': fallback_skill_calls,
                'avg_skill_cost_ms': avg_cost_ms,
                'workflow_runs': len(workflows),
                'workflow_failed_runs': workflow_failed,
            },
            'recommendation': {
                'kpis': overview['kpis'],
                'funnel': funnel['funnel'],
                'by_scene': funnel['by_scene'],
            },
            'users': {
                'summary': profiles['summary'],
                'strong_intent_distribution': strong_intent_users,
                'top_tags': profiles['top_tags'],
            },
            'products': {
                'high_value_products': high_value_products,
                'risk_products': risk_products,
            },
            'inventory': {
                'summary': inventory['summary'],
                'low_stock_products': low_stock_products,
            },
            'replenishment': replenishment,
            'mcp': {
                'skill_call_health': {
                    'total': len(skill_calls),
                    'failed': failed_skill_calls,
                    'fallback': fallback_skill_calls,
                    'avg_cost_ms': avg_cost_ms,
                },
                'recent_workflows': [
                    {
                        'workflow_name': row.get('workflow_name'),
                        'run_id': row.get('run_id'),
                        'request_id': row.get('request_id'),
                        'status': row.get('status'),
                        'created_at': row.get('created_at').isoformat() if row.get('created_at') else None,
                    }
                    for row in workflows[:filters['limit']]
                ],
            },
        }
