from app.skills.recommendation_skill import RecommendationSkill


def test_cosine_similarity_ranks_matching_product_first():
    skill = RecommendationSkill()
    result = skill.execute({
        'profile_tags': {'running': 3, 'summer': 1},
        'preferred_categories': {'C1': 2},
        'products': [
            {'product_id': 'P1', 'name': 'Running Shoes', 'category_id': 'C1', 'tags': ['running', 'summer'], 'tag_vector': {'running': 1, 'summer': 1}, 'gross_margin': 0.5, 'created_at': '2026-06-08T00:00:00'},
            {'product_id': 'P2', 'name': 'Winter Jacket', 'category_id': 'C2', 'tags': ['winter'], 'tag_vector': {'winter': 1}, 'gross_margin': 0.4, 'created_at': '2026-06-08T00:00:00'},
        ]
    })

    assert result['items'][0]['product']['product_id'] == 'P1'
    assert result['items'][0]['cosine_similarity'] > result['items'][1]['cosine_similarity']


def test_empty_user_vector_uses_cold_start_strategy():
    skill = RecommendationSkill()
    result = skill.execute({
        'profile_tags': {},
        'preferred_categories': {},
        'products': [
            {'product_id': 'P1', 'name': 'Popular Product', 'category_id': 'C1', 'tags': ['a'], 'tag_vector': {'a': 1}, 'gross_margin': 0.6, 'effective_stock': 50, 'popularity_score': 0.8, 'created_at': '2026-06-08T00:00:00'},
            {'product_id': 'P2', 'name': 'Less Popular', 'category_id': 'C2', 'tags': ['b'], 'tag_vector': {'b': 1}, 'gross_margin': 0.3, 'effective_stock': 10, 'popularity_score': 0.1, 'created_at': '2026-06-08T00:00:00'},
        ]
    })

    assert result['cold_start'] is True
    assert result['strategy'] == 'recommendation'
    assert result['items'][0]['product']['product_id'] == 'P1'
