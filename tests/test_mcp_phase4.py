from app.core.mcp import mcp_dispatcher, skill_registry
from app.core.database import get_mongo_db


def test_default_skills_are_registered(app):
    with app.app_context():
        names = {row['name'] for row in skill_registry.list_skills()}
        assert {'recommendation', 'product_selection', 'inventory_warning', 'replenishment'}.issubset(names)


def test_mcp_call_returns_standard_response_and_writes_log(app):
    with app.app_context():
        response = mcp_dispatcher.call(
            'inventory_warning',
            {'items': [{
                'product_id': 'P1',
                'available_stock': 0,
                'locked_stock': 0,
                'in_transit_stock': 0,
                'safe_stock': 5,
                'daily_sales': 2,
                'product_status': 'active',
            }]},
            tenant_id='T1',
            merchant_id='M1',
            request_id='REQ_MCP_1',
        )

        assert response['success'] is True
        assert response['code'] == 'OK'
        assert response['data']['items'][0]['warning_level'] == 'critical'

        mongo_db = get_mongo_db()
        log = mongo_db.skill_call_logs.find_one({'tenant_id': 'T1', 'merchant_id': 'M1', 'request_id': 'REQ_MCP_1'})
        assert log is not None
        assert log['skill_name'] == 'inventory_warning'
        assert log['status'] == 'success'
        assert isinstance(log['cost_ms'], int)


def test_mcp_skill_list_endpoint(client):
    response = client.get('/api/mcp/skills', query_string={'request_id': 'REQ_MCP_LIST'})
    assert response.status_code == 200
    body = response.get_json()
    assert body['success'] is True
    assert any(item['name'] == 'replenishment' for item in body['data']['items'])
