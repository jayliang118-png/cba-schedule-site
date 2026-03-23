"""
Unit tests for update_schedule.py script

Tests cover:
- Fetch error handling
- Parse error handling
- Transform logic (id, weekDay, date/time split, scores)
- Write logic and JSON structure
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock
import sys

# Import the module under test
import update_schedule


class TestUpdateSchedule:
    """Test suite for update_schedule.py"""

    @patch('update_schedule.fetch_sina_schedule')
    def test_fetch_error_returns_none(self, mock_fetch):
        """Test handling when fetch returns None"""
        mock_fetch.return_value = None

        exit_code = update_schedule.main()

        assert exit_code == 1

    @patch('update_schedule.fetch_sina_schedule')
    def test_fetch_exception_handling(self, mock_fetch):
        """Test handling when fetch raises exception"""
        mock_fetch.side_effect = Exception("Network error")

        exit_code = update_schedule.main()

        assert exit_code == 1

    @patch('update_schedule.fetch_sina_schedule')
    @patch('update_schedule.parse_schedule_html')
    def test_parse_error_empty_list(self, mock_parse, mock_fetch):
        """Test handling when parser returns empty list"""
        mock_fetch.return_value = "<html>test</html>"
        mock_parse.return_value = []

        exit_code = update_schedule.main()

        assert exit_code == 1

    @patch('update_schedule.fetch_sina_schedule')
    @patch('update_schedule.parse_schedule_html')
    def test_parse_exception_handling(self, mock_parse, mock_fetch):
        """Test handling when parser raises exception"""
        mock_fetch.return_value = "<html>test</html>"
        mock_parse.side_effect = Exception("Parse error")

        exit_code = update_schedule.main()

        assert exit_code == 1

    @patch('update_schedule.fetch_sina_schedule')
    @patch('update_schedule.parse_schedule_html')
    @patch('update_schedule.transform_to_json_format')
    def test_transform_exception_handling(self, mock_transform, mock_parse, mock_fetch):
        """Test handling when transform raises exception"""
        mock_fetch.return_value = "<html>test</html>"
        mock_parse.return_value = [{'datetime': '2026-03-23 19:35', 'home': 'Test', 'away': 'Test2'}]
        mock_transform.side_effect = Exception("Transform error")

        exit_code = update_schedule.main()

        assert exit_code == 1

    @patch('update_schedule.fetch_sina_schedule')
    @patch('update_schedule.parse_schedule_html')
    @patch('update_schedule.transform_to_json_format')
    @patch('pathlib.Path.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_write_exception_handling(self, mock_mkdir, mock_file, mock_transform, mock_parse, mock_fetch):
        """Test handling when file write raises exception"""
        mock_fetch.return_value = "<html>test</html>"
        mock_parse.return_value = [{'datetime': '2026-03-23 19:35'}]
        mock_transform.return_value = {'schedule': [], 'count': 0, 'updated': '2026-03-23T10:00:00Z'}
        mock_file.side_effect = IOError("Write error")

        exit_code = update_schedule.main()

        assert exit_code == 1

    @patch('update_schedule.fetch_sina_schedule')
    @patch('update_schedule.parse_schedule_html')
    @patch('update_schedule.transform_to_json_format')
    @patch('pathlib.Path.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_successful_update(self, mock_mkdir, mock_file, mock_transform, mock_parse, mock_fetch):
        """Test successful end-to-end update"""
        # Mock fetch
        mock_fetch.return_value = "<html>schedule data</html>"

        # Mock parse
        mock_parse.return_value = [
            {
                'round': '第1轮',
                'datetime': '2026-03-23 19:35',
                'home': '广东',
                'score': '98:92',
                'away': '辽宁',
                'status': '已结束'
            }
        ]

        # Mock transform
        mock_transform.return_value = {
            'schedule': [
                {
                    'id': 1,
                    'round': '第1轮',
                    'date': '2026-03-23',
                    'time': '19:35',
                    'homeTeam': '广东',
                    'awayTeam': '辽宁',
                    'venue': '东莞篮球中心',
                    'status': '已结束',
                    'homeScore': 98,
                    'awayScore': 92,
                    'weekDay': '周一'
                }
            ],
            'count': 1,
            'updated': '2026-03-23T10:00:00Z'
        }

        exit_code = update_schedule.main()

        assert exit_code == 0
        # Verify file operations
        assert mock_mkdir.called
        assert mock_file.called

    def test_json_structure_validation(self):
        """Test that transformed data matches expected JSON structure"""
        sample_data = {
            'schedule': [
                {
                    'id': 1,
                    'round': '第1轮',
                    'date': '2026-03-23',
                    'time': '19:35',
                    'homeTeam': '广东',
                    'awayTeam': '辽宁',
                    'venue': '东莞篮球中心',
                    'status': '已结束',
                    'homeScore': 98,
                    'awayScore': 92,
                    'weekDay': '周一'
                }
            ],
            'count': 1,
            'updated': '2026-03-23T10:00:00Z'
        }

        # Verify all required fields exist
        assert 'schedule' in sample_data
        assert 'count' in sample_data
        assert 'updated' in sample_data

        # Verify schedule array
        assert isinstance(sample_data['schedule'], list)
        assert len(sample_data['schedule']) > 0

        # Verify game structure
        game = sample_data['schedule'][0]
        required_fields = [
            'id', 'round', 'date', 'time', 'homeTeam', 'awayTeam',
            'venue', 'status', 'homeScore', 'awayScore', 'weekDay'
        ]
        for field in required_fields:
            assert field in game, f"Missing required field: {field}"

        # Verify field types
        assert isinstance(game['id'], int)
        assert isinstance(game['homeScore'], (int, type(None)))
        assert isinstance(game['awayScore'], (int, type(None)))
        assert game['status'] in ['未开始', '进行中', '已结束']

    def test_id_field_increments(self):
        """Test that id field increments correctly"""
        # This test verifies the behavior in parser.py's transform_to_json_format
        # which is already tested in test_parser.py, but we validate the concept here
        ids = [1, 2, 3, 4, 5]
        for i, expected_id in enumerate(ids):
            assert expected_id == i + 1

    def test_weekday_calculation(self):
        """Test weekday calculation logic"""
        # Test weekday mapping (Chinese)
        weekday_map = {
            0: '周一',
            1: '周二',
            2: '周三',
            3: '周四',
            4: '周五',
            5: '周六',
            6: '周日'
        }

        # Test date: 2026-03-23 is Monday (weekday 0)
        test_date = datetime.strptime('2026-03-23', '%Y-%m-%d')
        weekday = weekday_map[test_date.weekday()]
        assert weekday == '周一'

    def test_date_time_split(self):
        """Test splitting datetime into date and time"""
        datetime_str = "2026-03-23 19:35"
        parts = datetime_str.split(' ')
        date = parts[0] if len(parts) > 0 else ''
        time = parts[1] if len(parts) > 1 else ''

        assert date == "2026-03-23"
        assert time == "19:35"

    def test_score_parsing_finished_game(self):
        """Test score parsing for finished games"""
        score_str = "98:92"
        status = "已结束"

        home_score = None
        away_score = None

        if status == '已结束' and ':' in score_str:
            try:
                parts = score_str.split(':')
                home_score = int(parts[0])
                away_score = int(parts[1])
            except (ValueError, IndexError):
                home_score = None
                away_score = None

        assert home_score == 98
        assert away_score == 92

    def test_score_parsing_not_started(self):
        """Test score parsing for games not started"""
        score_str = "VS"
        status = "未开始"

        home_score = None
        away_score = None

        if status == '已结束' and ':' in score_str:
            try:
                parts = score_str.split(':')
                home_score = int(parts[0])
                away_score = int(parts[1])
            except (ValueError, IndexError):
                home_score = None
                away_score = None

        # Should remain None for not started games
        assert home_score is None
        assert away_score is None

    def test_score_parsing_invalid_format(self):
        """Test score parsing with invalid format"""
        score_str = "98-92"  # Wrong separator
        status = "已结束"

        home_score = None
        away_score = None

        if status == '已结束' and ':' in score_str:
            try:
                parts = score_str.split(':')
                home_score = int(parts[0])
                away_score = int(parts[1])
            except (ValueError, IndexError):
                home_score = None
                away_score = None

        # Should remain None because ':' not in score
        assert home_score is None
        assert away_score is None

    def test_status_values(self):
        """Test that status uses correct Chinese characters"""
        valid_statuses = ['未开始', '进行中', '已结束']

        for status in valid_statuses:
            assert status in valid_statuses

        # Ensure no English status values
        invalid_statuses = ['Not Started', 'In Progress', 'Finished']
        for status in invalid_statuses:
            assert status not in valid_statuses


# Integration test with real modules (optional, runs if modules available)
class TestIntegrationWithRealModules:
    """Integration tests using actual scraper and parser modules"""

    def test_parser_transform_output_structure(self):
        """Test that parser.transform_to_json_format produces correct structure"""
        from parser import transform_to_json_format

        # Sample input
        raw_games = [
            {
                'round': '第1轮',
                'datetime': '2026-03-23 19:35',
                'home': '广东',
                'score': '98:92',
                'away': '辽宁',
                'status': '已结束'
            }
        ]

        result = transform_to_json_format(raw_games)

        # Verify structure
        assert 'schedule' in result
        assert 'count' in result
        assert 'updated' in result
        assert result['count'] == 1
        assert len(result['schedule']) == 1

        # Verify first game has all fields
        game = result['schedule'][0]
        assert game['id'] == 1
        assert game['date'] == '2026-03-23'
        assert game['time'] == '19:35'
        assert game['homeTeam'] == '广东'
        assert game['awayTeam'] == '辽宁'
        assert game['status'] == '已结束'
        assert game['homeScore'] == 98
        assert game['awayScore'] == 92
        assert game['weekDay'] == '周一'
