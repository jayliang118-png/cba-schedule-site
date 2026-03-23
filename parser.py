"""
Sina Sports HTML Parser
Extracts game data from HTML tables (DATA-02)
"""

from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
import json


def parse_schedule_html(html: str) -> List[Dict]:
    """
    Parse Sina Sports HTML to extract game schedule data.

    Args:
        html: Decoded HTML string from Sina Sports

    Returns:
        List of game dictionaries with keys:
        - round: str (e.g., "第1轮" or empty if not available)
        - datetime: str (e.g., "2025-10-20 19:35")
        - home: str (home team name)
        - score: str (e.g., "98:92" or "VS")
        - away: str (away team name)
        - status: str ("未开始", "进行中", "已结束")
    """
    soup = BeautifulSoup(html, 'lxml')

    # Find all schedule rows (odd and even classes) - they're not in a specific container
    rows = soup.find_all('tr', class_=['odd', 'even'])

    schedule = []
    for row in rows:
        # Extract all cells from this row
        cells = row.find_all('td')

        # Skip header rows (th elements instead of td)
        if len(cells) < 4:
            continue

        # Extract text from each cell and clean it
        cell_texts = [cell.get_text(strip=True).replace('\xa0', ' ') for cell in cells]

        # Current Sina structure: date, home, score, away (4 columns, no round)
        datetime_text = cell_texts[0]
        home = cell_texts[1]
        score = cell_texts[2]
        away = cell_texts[3]

        # Determine game status (matching update_schedule.js lines 64-74)
        today = datetime.now().date().isoformat()
        game_date = datetime_text.split(' ')[0] if ' ' in datetime_text else datetime_text

        if ':' in score and 'VS' not in score:
            status = '已结束'
        elif game_date == today:
            status = '进行中'
        elif game_date < today:
            status = '已结束'
        else:
            status = '未开始'

        schedule.append({
            'round': '',  # Current Sina HTML doesn't include round info
            'datetime': datetime_text,
            'home': home,
            'score': score,
            'away': away,
            'status': status
        })

    return schedule


def transform_to_json_format(raw_games: List[Dict]) -> Dict:
    """
    Transform parsed games into final JSON structure for storage.

    Args:
        raw_games: List of game dicts from parse_schedule_html()

    Returns:
        Dict with structure:
        {
            "schedule": [...games with expanded fields...],
            "updated": "2026-03-23T10:30:00Z",
            "count": 100
        }
    """
    # Weekday mapping (Chinese)
    weekday_map = {
        0: '周一',
        1: '周二',
        2: '周三',
        3: '周四',
        4: '周五',
        5: '周六',
        6: '周日'
    }

    # Team venue mapping (from app.py)
    TEAM_VENUES = {
        '广东': '东莞篮球中心', '辽宁': '辽宁体育馆', '浙江': '义乌梅湖体育馆',
        '新疆': '乌鲁木齐奥体中心', '北京': '五棵松体育馆', '上海': '梅赛德斯奔驰文化中心',
        '山东': '济南奥体中心', '深圳': '深圳大运中心体育馆', '广州': '天河体育馆',
        '北控': '国家体育馆', '江苏': '苏州体育中心', '福建': '晋江祖昌体育馆',
        '广厦': '诸暨暨阳学院体育馆', '青岛': '青岛国信体育馆', '四川': '成都金强体育馆',
        '天津': '东丽体育馆', '同曦': '南京青奥体育公园体育馆', '宁波': '宁波奥体中心',
        '吉林': '长春市体育馆', '山西': '山西省体育中心'
    }

    expanded_schedule = []

    for idx, game in enumerate(raw_games, start=1):
        # Split datetime into date and time
        datetime_parts = game['datetime'].split(' ')
        date = datetime_parts[0] if len(datetime_parts) > 0 else ''
        time = datetime_parts[1] if len(datetime_parts) > 1 else ''

        # Calculate weekday from date
        weekday = ''
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                weekday = weekday_map[date_obj.weekday()]
            except ValueError:
                weekday = ''

        # Parse score into homeScore/awayScore integers (if game finished)
        home_score = None
        away_score = None
        if game['status'] == '已结束' and ':' in game['score']:
            try:
                score_parts = game['score'].split(':')
                home_score = int(score_parts[0])
                away_score = int(score_parts[1])
            except (ValueError, IndexError):
                pass

        # Lookup venue by home team
        venue = TEAM_VENUES.get(game['home'], '')

        expanded_schedule.append({
            'id': idx,
            'round': game['round'],
            'date': date,
            'time': time,
            'homeTeam': game['home'],
            'awayTeam': game['away'],
            'venue': venue,
            'status': game['status'],
            'homeScore': home_score,
            'awayScore': away_score,
            'weekDay': weekday
        })

    return {
        'schedule': expanded_schedule,
        'updated': datetime.now().astimezone().isoformat(),
        'count': len(expanded_schedule)
    }


if __name__ == '__main__':
    """Test the parser with real data from Sina Sports"""
    print("Testing Sina Sports Parser...")
    print("=" * 60)

    # Import scraper to fetch HTML
    from scraper import fetch_sina_schedule

    html = fetch_sina_schedule()

    if not html:
        print("FAILURE: Could not fetch HTML from Sina Sports")
        exit(1)

    # Parse HTML
    print("\n" + "=" * 60)
    print("Parsing HTML with BeautifulSoup...")
    raw_games = parse_schedule_html(html)
    print(f"Extracted {len(raw_games)} games")

    if len(raw_games) == 0:
        print("FAILURE: No games extracted from HTML")
        exit(1)

    # Transform to JSON format
    print("\n" + "=" * 60)
    print("Transforming to JSON format...")
    data = transform_to_json_format(raw_games)
    print(f"Transformed {data['count']} games")

    # Display first 3 games
    print("\n" + "=" * 60)
    print("First 3 games:")
    print("-" * 60)
    for game in data['schedule'][:3]:
        print(json.dumps(game, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("SUCCESS: Parser working correctly")
    print(f"Total games: {data['count']}")
    print(f"Updated: {data['updated']}")
    print("=" * 60)
