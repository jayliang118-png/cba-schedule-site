"""
Unit tests for parser.py
Tests HTML parsing edge cases and data transformation (QA-01)
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from parser import parse_schedule_html, transform_to_json_format
from datetime import datetime


# Test fixtures
@pytest.fixture
def sample_html_valid():
    """Valid Sina Sports HTML sample"""
    return """
    <html>
    <body>
    <div class="part part02">
        <table>
            <tr class="odd">
                <td>2025-10-20 19:35</td>
                <td><a>广东</a></td>
                <td><a>98 : 92</a></td>
                <td><a>辽宁</a></td>
            </tr>
        </table>
    </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_missing_score():
    """HTML with missing score (upcoming game)"""
    return """
    <html>
    <body>
    <div class="part part02">
        <table>
            <tr class="odd">
                <td>2026-06-01 19:35</td>
                <td><a>北京</a></td>
                <td><a>VS</a></td>
                <td><a>上海</a></td>
            </tr>
        </table>
    </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_malformed_date():
    """HTML with malformed date format"""
    return """
    <html>
    <body>
    <div class="part part02">
        <table>
            <tr class="odd">
                <td>2025-10-2019:35</td>
                <td><a>广东</a></td>
                <td><a>98:92</a></td>
                <td><a>辽宁</a></td>
            </tr>
        </table>
    </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_empty_table():
    """HTML with empty schedule table"""
    return """<div class="part part02"><table></table></div>"""


@pytest.fixture
def sample_html_today_game():
    """HTML with game scheduled for today"""
    today = datetime.now().date().isoformat()
    return f"""
    <html>
    <body>
    <div class="part part02">
        <table>
            <tr class="even">
                <td>{today} 19:35</td>
                <td><a>新疆</a></td>
                <td><a>VS</a></td>
                <td><a>山东</a></td>
            </tr>
        </table>
    </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_past_game_no_score():
    """HTML with past game but missing score"""
    return """
    <html>
    <body>
    <div class="part part02">
        <table>
            <tr class="odd">
                <td>2024-01-15 19:35</td>
                <td><a>福建</a></td>
                <td><a>VS</a></td>
                <td><a>青岛</a></td>
            </tr>
        </table>
    </div>
    </body>
    </html>
    """


# Test cases for parse_schedule_html()

def test_parse_schedule_html_valid(sample_html_valid):
    """Test parsing valid HTML returns correct game structure"""
    games = parse_schedule_html(sample_html_valid)
    assert len(games) == 1
    assert games[0]['round'] == ''  # Current Sina HTML doesn't include round
    assert games[0]['datetime'] == '2025-10-20 19:35'
    assert games[0]['home'] == '广东'
    assert games[0]['score'] == '98 : 92'
    assert games[0]['away'] == '辽宁'
    assert games[0]['status'] == '已结束'


def test_parse_schedule_html_missing_score(sample_html_missing_score):
    """Test parsing handles missing score (upcoming game)"""
    games = parse_schedule_html(sample_html_missing_score)
    assert len(games) == 1
    assert games[0]['score'] == 'VS'
    assert games[0]['status'] == '未开始'


def test_parse_schedule_html_empty_table(sample_html_empty_table):
    """Test parsing empty table returns empty list"""
    games = parse_schedule_html(sample_html_empty_table)
    assert games == []


def test_parse_schedule_html_malformed_date(sample_html_malformed_date):
    """Test parser handles malformed date gracefully"""
    # Should not crash, either parse or skip row
    games = parse_schedule_html(sample_html_malformed_date)
    # Either successfully parsed with date correction, or skipped row
    assert isinstance(games, list)


def test_parse_schedule_html_status_today_game(sample_html_today_game):
    """Test status logic - game today is marked 进行中"""
    games = parse_schedule_html(sample_html_today_game)
    assert len(games) == 1
    assert games[0]['status'] == '进行中'


def test_parse_schedule_html_status_past_no_score(sample_html_past_game_no_score):
    """Test status logic - past game without score is marked 已结束"""
    games = parse_schedule_html(sample_html_past_game_no_score)
    assert len(games) == 1
    # Past date should be marked as 已结束 even if score is VS
    assert games[0]['status'] == '已结束'


def test_parse_schedule_html_multiple_games():
    """Test parsing multiple games in one HTML"""
    html = """
    <html>
    <body>
        <table>
            <tr class="odd">
                <td>2025-10-20 19:35</td>
                <td><a>广东</a></td>
                <td><a>98:92</a></td>
                <td><a>辽宁</a></td>
            </tr>
            <tr class="even">
                <td>2025-10-21 19:35</td>
                <td><a>北京</a></td>
                <td><a>85:80</a></td>
                <td><a>上海</a></td>
            </tr>
            <tr class="odd">
                <td>2026-06-01 19:35</td>
                <td><a>新疆</a></td>
                <td><a>VS</a></td>
                <td><a>山东</a></td>
            </tr>
        </table>
    </body>
    </html>
    """
    games = parse_schedule_html(html)
    assert len(games) == 3
    assert games[0]['status'] == '已结束'
    assert games[1]['status'] == '已结束'
    assert games[2]['status'] == '未开始'


def test_parse_schedule_html_insufficient_columns():
    """Test parser skips rows with insufficient columns"""
    html = """
    <html>
    <body>
        <table>
            <tr class="odd">
                <td>Header 1</td>
                <td>Header 2</td>
            </tr>
            <tr class="even">
                <td>2025-10-20 19:35</td>
                <td><a>广东</a></td>
                <td><a>98:92</a></td>
                <td><a>辽宁</a></td>
            </tr>
        </table>
    </body>
    </html>
    """
    games = parse_schedule_html(html)
    # Should only parse the valid row, skip the header row
    assert len(games) == 1
    assert games[0]['home'] == '广东'


# Test cases for transform_to_json_format()

def test_transform_to_json_format_structure():
    """Test transformation adds all required fields"""
    raw_games = [{
        'round': '第1轮',
        'datetime': '2025-10-20 19:35',
        'home': '广东',
        'score': '98:92',
        'away': '辽宁',
        'status': '已结束'
    }]

    data = transform_to_json_format(raw_games)

    assert 'schedule' in data
    assert 'updated' in data
    assert 'count' in data
    assert data['count'] == 1

    game = data['schedule'][0]
    assert 'id' in game
    assert 'date' in game
    assert 'time' in game
    assert 'weekDay' in game
    assert 'homeTeam' in game
    assert 'awayTeam' in game
    assert 'venue' in game
    assert 'homeScore' in game
    assert 'awayScore' in game


def test_transform_weekday_calculation():
    """Test weekDay field is correctly calculated"""
    # 2025-10-20 is a Monday (周一)
    raw_games = [{
        'round': '第1轮',
        'datetime': '2025-10-20 19:35',
        'home': '广东',
        'score': 'VS',
        'away': '辽宁',
        'status': '未开始'
    }]

    data = transform_to_json_format(raw_games)
    assert data['schedule'][0]['weekDay'] == '周一'


def test_transform_score_parsing():
    """Test score string is split into homeScore and awayScore integers"""
    raw_games = [{
        'round': '第1轮',
        'datetime': '2025-10-20 19:35',
        'home': '广东',
        'score': '98:92',
        'away': '辽宁',
        'status': '已结束'
    }]

    data = transform_to_json_format(raw_games)
    game = data['schedule'][0]
    assert game['homeScore'] == 98
    assert game['awayScore'] == 92
    assert isinstance(game['homeScore'], int)


def test_transform_score_vs():
    """Test 'VS' score results in None for homeScore/awayScore"""
    raw_games = [{
        'round': '第1轮',
        'datetime': '2025-10-20 19:35',
        'home': '广东',
        'score': 'VS',
        'away': '辽宁',
        'status': '未开始'
    }]

    data = transform_to_json_format(raw_games)
    game = data['schedule'][0]
    assert game['homeScore'] is None
    assert game['awayScore'] is None


def test_transform_venue_lookup():
    """Test venue is correctly looked up from TEAM_VENUES"""
    # Home team is 广东, venue should be 东莞篮球中心
    raw_games = [{
        'round': '第1轮',
        'datetime': '2025-10-20 19:35',
        'home': '广东',
        'score': 'VS',
        'away': '辽宁',
        'status': '未开始'
    }]

    data = transform_to_json_format(raw_games)
    assert data['schedule'][0]['venue'] == '东莞篮球中心'


def test_transform_venue_missing_team():
    """Test venue lookup handles unknown team gracefully"""
    raw_games = [{
        'round': '第1轮',
        'datetime': '2025-10-20 19:35',
        'home': '未知球队',
        'score': 'VS',
        'away': '辽宁',
        'status': '未开始'
    }]

    data = transform_to_json_format(raw_games)
    # Should return empty string for unknown team
    assert data['schedule'][0]['venue'] == ''


def test_transform_datetime_splitting():
    """Test datetime is correctly split into date and time"""
    raw_games = [{
        'round': '',
        'datetime': '2025-10-20 19:35',
        'home': '广东',
        'score': 'VS',
        'away': '辽宁',
        'status': '未开始'
    }]

    data = transform_to_json_format(raw_games)
    game = data['schedule'][0]
    assert game['date'] == '2025-10-20'
    assert game['time'] == '19:35'


def test_transform_sequential_ids():
    """Test games are assigned sequential IDs starting from 1"""
    raw_games = [
        {
            'round': '',
            'datetime': '2025-10-20 19:35',
            'home': '广东',
            'score': '98:92',
            'away': '辽宁',
            'status': '已结束'
        },
        {
            'round': '',
            'datetime': '2025-10-21 19:35',
            'home': '北京',
            'score': '85:80',
            'away': '上海',
            'status': '已结束'
        }
    ]

    data = transform_to_json_format(raw_games)
    assert data['schedule'][0]['id'] == 1
    assert data['schedule'][1]['id'] == 2


def test_transform_invalid_date():
    """Test transformation handles invalid date format gracefully"""
    raw_games = [{
        'round': '',
        'datetime': 'invalid-date 19:35',
        'home': '广东',
        'score': 'VS',
        'away': '辽宁',
        'status': '未开始'
    }]

    data = transform_to_json_format(raw_games)
    # Should not crash, weekDay should be empty
    assert data['schedule'][0]['weekDay'] == ''


def test_transform_score_with_spaces():
    """Test score parsing handles spaces around colon"""
    raw_games = [{
        'round': '',
        'datetime': '2025-10-20 19:35',
        'home': '广东',
        'score': '98 : 92',
        'away': '辽宁',
        'status': '已结束'
    }]

    data = transform_to_json_format(raw_games)
    game = data['schedule'][0]
    # Should still parse correctly despite spaces
    assert game['homeScore'] == 98
    assert game['awayScore'] == 92


def test_transform_malformed_score():
    """Test score parsing handles malformed score gracefully"""
    raw_games = [{
        'round': '',
        'datetime': '2025-10-20 19:35',
        'home': '广东',
        'score': '98:abc',
        'away': '辽宁',
        'status': '已结束'
    }]

    data = transform_to_json_format(raw_games)
    game = data['schedule'][0]
    # Should fall back to None if parsing fails
    assert game['homeScore'] is None
    assert game['awayScore'] is None


def test_transform_empty_list():
    """Test transformation handles empty game list"""
    raw_games = []
    data = transform_to_json_format(raw_games)

    assert data['schedule'] == []
    assert data['count'] == 0
    assert 'updated' in data
