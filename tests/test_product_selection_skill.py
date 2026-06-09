from app.skills.product_selection_skill import ProductSelectionSkill


def test_hot_product_classification():
    skill = ProductSelectionSkill()
    result = skill.execute({'products': [{
        'product_id': 'P1',
        'name': 'Hot Product',
        'status': 'active',
        'gross_margin': 0.5,
        'effective_stock': 20,
        'safe_stock': 5,
        'metrics': {
            'exposure_count': 100,
            'click_count': 25,
            'add_cart_count': 12,
            'convert_count': 4,
        },
        'has_feedback': True,
    }]})

    item = result['items'][0]
    assert item['layer'] == 'hot'
    assert 'increase_exposure' in item['advice']


def test_risk_product_classification_for_no_stock():
    skill = ProductSelectionSkill()
    result = skill.execute({'products': [{
        'product_id': 'P1',
        'name': 'Risk Product',
        'status': 'active',
        'gross_margin': 0.2,
        'effective_stock': 0,
        'safe_stock': 5,
        'metrics': {
            'exposure_count': 10,
            'click_count': 1,
            'add_cart_count': 0,
            'convert_count': 0,
        },
        'has_feedback': True,
    }]})

    item = result['items'][0]
    assert item['layer'] == 'risk'
    assert 'restock_or_hide' in item['advice']
