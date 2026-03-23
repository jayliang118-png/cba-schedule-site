"""
Filter Service for CBA Schedule Data
Provides pure filter functions for schedule filtering by date, team, and status.
All functions follow immutable patterns - no mutations, return new lists.
"""

from typing import List, Dict, Optional, Any


def filter_by_date(games: List[Dict[str, Any]], date_str: str) -> List[Dict[str, Any]]:
    """
    Filter games by exact date match.

    Args:
        games: List of game dictionaries with 'date' field (YYYY-MM-DD format)
        date_str: Date string in YYYY-MM-DD format to filter by

    Returns:
        New list containing only games matching the specified date.
        If date_str is empty or None, returns all games (no filter).
    """
    if not date_str:
        return games

    return [game for game in games if game.get('date') == date_str]


def filter_by_team(games: List[Dict[str, Any]], team_name: str) -> List[Dict[str, Any]]:
    """
    Filter games by team (home or away).

    Args:
        games: List of game dictionaries with 'homeTeam' and 'awayTeam' fields
        team_name: Team name string to filter by

    Returns:
        New list containing only games where team_name matches either
        homeTeam or awayTeam. If team_name is empty or None, returns all games.
    """
    if not team_name:
        return games

    return [
        game for game in games
        if game.get('homeTeam') == team_name or game.get('awayTeam') == team_name
    ]


def filter_by_status(games: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    """
    Filter games by status.

    Args:
        games: List of game dictionaries with 'status' field
        status: Status string to filter by ('未开始', '进行中', '已结束')

    Returns:
        New list containing only games matching the specified status.
        If status is empty or None, returns all games (no filter).
    """
    if not status:
        return games

    return [game for game in games if game.get('status') == status]


def apply_filters(
    games: List[Dict[str, Any]],
    date: Optional[str] = None,
    team: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Apply multiple filters to games list using intersection logic (AND).

    This function chains filters together: games -> date filter -> team filter -> status filter.
    Each filter creates a new list without mutating the input.

    Args:
        games: List of game dictionaries to filter
        date: Optional date string in YYYY-MM-DD format
        team: Optional team name string
        status: Optional status string ('未开始', '进行中', '已结束')

    Returns:
        New list with all filters applied. Empty filters are skipped (treated as "no filter").
        If all filters are empty/None, returns the original games list unchanged.

    Example:
        >>> games = [
        ...     {'date': '2026-03-23', 'homeTeam': '广东', 'status': '进行中'},
        ...     {'date': '2026-03-23', 'homeTeam': '辽宁', 'status': '已结束'},
        ...     {'date': '2026-03-24', 'homeTeam': '广东', 'status': '未开始'}
        ... ]
        >>> apply_filters(games, date='2026-03-23', team='广东')
        [{'date': '2026-03-23', 'homeTeam': '广东', 'status': '进行中'}]
    """
    # Chain filters: each filter operates on result of previous filter
    filtered = games
    filtered = filter_by_date(filtered, date or '')
    filtered = filter_by_team(filtered, team or '')
    filtered = filter_by_status(filtered, status or '')

    return filtered
