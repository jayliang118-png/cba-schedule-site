"""
Integration tests for filter_service.py and /api/schedule endpoint
Tests all filter combinations, edge cases, and API integration (QA-02, QA-03)
"""

import pytest
from app import app
from filter_service import filter_by_date, filter_by_team, filter_by_status, apply_filters


@pytest.fixture
def client():
    """Flask test client for integration tests"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_games():
    """Sample game data for unit tests"""
    return [
        {
            'id': 1,
            'date': '2026-03-22',
            'homeTeam': '广东',
            'awayTeam': '辽宁',
            'status': '已结束',
            'homeScore': 100,
            'awayScore': 95
        },
        {
            'id': 2,
            'date': '2026-03-23',
            'homeTeam': '北京',
            'awayTeam': '广东',
            'status': '进行中',
            'homeScore': None,
            'awayScore': None
        },
        {
            'id': 3,
            'date': '2026-03-23',
            'homeTeam': '上海',
            'awayTeam': '浙江',
            'status': '未开始',
            'homeScore': None,
            'awayScore': None
        },
        {
            'id': 4,
            'date': '2026-03-24',
            'homeTeam': '新疆',
            'awayTeam': '辽宁',
            'status': '未开始',
            'homeScore': None,
            'awayScore': None
        },
    ]


# Unit Tests for filter_service.py

@pytest.mark.unit
def test_filter_by_date_single_match(sample_games):
    """Test date filter returns only games on specified date"""
    result = filter_by_date(sample_games, '2026-03-22')
    assert len(result) == 1, "Expected 1 game on 2026-03-22"
    assert result[0]['date'] == '2026-03-22'
    assert result[0]['homeTeam'] == '广东'


@pytest.mark.unit
def test_filter_by_date_multiple_matches(sample_games):
    """Test date filter handles multiple games on same date"""
    result = filter_by_date(sample_games, '2026-03-23')
    assert len(result) == 2, "Expected 2 games on 2026-03-23"
    assert all(game['date'] == '2026-03-23' for game in result), "All games should be on 2026-03-23"


@pytest.mark.unit
def test_filter_by_date_no_matches(sample_games):
    """Test date filter returns empty list for non-existent date"""
    result = filter_by_date(sample_games, '2026-12-31')
    assert len(result) == 0, "Expected no games on 2026-12-31"


@pytest.mark.unit
def test_filter_by_date_empty_string(sample_games):
    """Test empty date returns all games (no filter)"""
    result = filter_by_date(sample_games, '')
    assert len(result) == 4, "Expected all 4 games when date is empty"


@pytest.mark.unit
def test_filter_by_team_home(sample_games):
    """Test team filter finds team as home team"""
    result = filter_by_team(sample_games, '广东')
    assert len(result) >= 1, "Expected at least 1 game with 广东"
    assert any(game['homeTeam'] == '广东' for game in result), "广东 should be found as home team"


@pytest.mark.unit
def test_filter_by_team_away(sample_games):
    """Test team filter finds team as away team"""
    result = filter_by_team(sample_games, '辽宁')
    assert len(result) == 2, "Expected 2 games with 辽宁"
    assert all(game['homeTeam'] == '辽宁' or game['awayTeam'] == '辽宁' for game in result)


@pytest.mark.unit
def test_filter_by_team_multiple(sample_games):
    """Test team filter finds all games with team (home or away)"""
    result = filter_by_team(sample_games, '广东')
    assert len(result) == 2, "Expected 2 games with 广东 (1 home, 1 away)"
    for game in result:
        assert game['homeTeam'] == '广东' or game['awayTeam'] == '广东', "广东 should be in each game"


@pytest.mark.unit
def test_filter_by_team_empty(sample_games):
    """Test empty team returns all games"""
    result = filter_by_team(sample_games, '')
    assert len(result) == 4, "Expected all 4 games when team is empty"


@pytest.mark.unit
def test_filter_by_status_finished(sample_games):
    """Test status filter for '已结束'"""
    result = filter_by_status(sample_games, '已结束')
    assert len(result) == 1, "Expected 1 finished game"
    assert result[0]['status'] == '已结束'


@pytest.mark.unit
def test_filter_by_status_in_progress(sample_games):
    """Test status filter for '进行中'"""
    result = filter_by_status(sample_games, '进行中')
    assert len(result) == 1, "Expected 1 in-progress game"
    assert result[0]['status'] == '进行中'


@pytest.mark.unit
def test_filter_by_status_not_started(sample_games):
    """Test status filter for '未开始'"""
    result = filter_by_status(sample_games, '未开始')
    assert len(result) == 2, "Expected 2 not-started games"
    assert all(game['status'] == '未开始' for game in result)


@pytest.mark.unit
def test_apply_filters_date_and_team(sample_games):
    """Test combined date + team filters (intersection)"""
    result = apply_filters(sample_games, date='2026-03-23', team='广东')
    assert len(result) == 1, "Expected 1 game on 2026-03-23 with 广东"
    assert result[0]['date'] == '2026-03-23'
    assert result[0]['awayTeam'] == '广东'


@pytest.mark.unit
def test_apply_filters_all_three(sample_games):
    """Test date + team + status filters combined"""
    result = apply_filters(sample_games, date='2026-03-23', team='广东', status='进行中')
    assert len(result) == 1, "Expected 1 game matching all criteria"
    assert result[0]['date'] == '2026-03-23'
    assert result[0]['awayTeam'] == '广东'
    assert result[0]['status'] == '进行中'


@pytest.mark.unit
def test_apply_filters_no_filters(sample_games):
    """Test apply_filters with no params returns all games"""
    result = apply_filters(sample_games)
    assert len(result) == 4, "Expected all 4 games when no filters provided"


# Integration Tests for /api/schedule endpoint

@pytest.mark.integration
def test_api_schedule_no_filters(client):
    """Test GET /api/schedule returns all games with success=true"""
    response = client.get('/api/schedule')
    assert response.status_code == 200, "Expected HTTP 200"

    data = response.get_json()
    assert data['success'] is True, "Expected success=true"
    assert 'data' in data, "Expected 'data' field"
    assert 'count' in data, "Expected 'count' field"
    assert 'updated' in data, "Expected 'updated' field"
    assert len(data['data']) > 0, "Expected at least 1 game in response"
    assert data['count'] == len(data['data']), "Count should match data length"


@pytest.mark.integration
def test_api_schedule_date_filter(client):
    """Test GET /api/schedule?date=2026-03-23 returns only March 23 games"""
    response = client.get('/api/schedule?date=2026-03-23')
    assert response.status_code == 200, "Expected HTTP 200"

    data = response.get_json()
    assert data['success'] is True, "Expected success=true"
    assert len(data['data']) > 0, "Expected games on 2026-03-23"
    assert all(game['date'] == '2026-03-23' for game in data['data']), "All games should be on 2026-03-23"


@pytest.mark.integration
def test_api_schedule_team_filter(client):
    """Test GET /api/schedule?team=广东 returns only 广东 games"""
    response = client.get('/api/schedule?team=广东')
    assert response.status_code == 200, "Expected HTTP 200"

    data = response.get_json()
    assert data['success'] is True, "Expected success=true"

    # Should find 广东 as home or away team
    for game in data['data']:
        assert game['homeTeam'] == '广东' or game['awayTeam'] == '广东', "广东 should be in each game"


@pytest.mark.integration
def test_api_schedule_status_filter(client):
    """Test GET /api/schedule?status=已结束 returns only finished games"""
    response = client.get('/api/schedule?status=已结束')
    assert response.status_code == 200, "Expected HTTP 200"

    data = response.get_json()
    assert data['success'] is True, "Expected success=true"

    # All games should have status='已结束'
    for game in data['data']:
        assert game['status'] == '已结束', "Expected only finished games"


@pytest.mark.integration
def test_api_schedule_multiple_filters(client):
    """Test GET /api/schedule with multiple filters returns intersection"""
    response = client.get('/api/schedule?date=2026-03-23&team=上海')
    assert response.status_code == 200, "Expected HTTP 200"

    data = response.get_json()
    assert data['success'] is True, "Expected success=true"

    # Should return games on 2026-03-23 with 上海
    for game in data['data']:
        assert game['date'] == '2026-03-23', "Expected date 2026-03-23"
        assert game['homeTeam'] == '上海' or game['awayTeam'] == '上海', "Expected 上海 in game"


@pytest.mark.integration
def test_api_schedule_invalid_date(client):
    """Test graceful handling of non-existent date (returns empty array)"""
    response = client.get('/api/schedule?date=2099-12-31')
    assert response.status_code == 200, "Expected HTTP 200 even for no results"

    data = response.get_json()
    assert data['success'] is True, "Expected success=true"
    assert len(data['data']) == 0, "Expected empty array for non-existent date"
    assert data['count'] == 0, "Expected count=0"


@pytest.mark.integration
def test_api_schedule_case_sensitive_team(client):
    """Test team names are case-sensitive (expect exact match)"""
    # Valid team name
    response1 = client.get('/api/schedule?team=广东')
    data1 = response1.get_json()

    # Invalid team name (wrong case or spelling)
    response2 = client.get('/api/schedule?team=guangdong')
    data2 = response2.get_json()

    # Valid query should return games, invalid should return empty
    assert len(data1['data']) > 0, "Expected games for valid team '广东'"
    assert len(data2['data']) == 0, "Expected no games for invalid team 'guangdong'"


@pytest.mark.integration
def test_api_response_structure(client):
    """Test response has {success, data, count, updated} structure"""
    response = client.get('/api/schedule')
    assert response.status_code == 200, "Expected HTTP 200"

    data = response.get_json()

    # Verify all required fields exist
    assert 'success' in data, "Missing 'success' field"
    assert 'data' in data, "Missing 'data' field"
    assert 'count' in data, "Missing 'count' field"
    assert 'updated' in data, "Missing 'updated' field"

    # Verify field types
    assert isinstance(data['success'], bool), "success should be boolean"
    assert isinstance(data['data'], list), "data should be list"
    assert isinstance(data['count'], int), "count should be integer"
    assert isinstance(data['updated'], str), "updated should be string"
