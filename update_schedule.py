#!/usr/bin/env python3
"""
CBA Schedule Update Script
Fetches latest schedule from Sina Sports and updates data/schedule.json

Usage: python update_schedule.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Import existing modules
from scraper import fetch_sina_schedule
from parser import parse_schedule_html, transform_to_json_format


def main():
    """
    Main function to fetch, parse, and update CBA schedule data.

    Process:
    1. Fetch HTML from Sina Sports (GBK encoded)
    2. Parse HTML to extract game data
    3. Transform to JSON format with expanded fields
    4. Write to data/schedule.json

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("=" * 60)
    print("CBA Schedule Update Script")
    print("=" * 60)
    print()

    # Step 1: Fetch HTML from Sina Sports
    print("[1/4] Fetching schedule from Sina Sports...")
    try:
        html = fetch_sina_schedule()
    except Exception as e:
        print(f"ERROR: Failed to fetch schedule: {e}")
        return 1

    if not html:
        print("ERROR: Could not fetch HTML from Sina Sports")
        return 1

    print(f"      Successfully fetched {len(html)} characters")
    print()

    # Step 2: Parse HTML to extract games
    print("[2/4] Parsing HTML to extract game data...")
    try:
        raw_games = parse_schedule_html(html)
    except Exception as e:
        print(f"ERROR: Failed to parse HTML: {e}")
        return 1

    if not raw_games:
        print("ERROR: No games found in HTML")
        return 1

    print(f"      Extracted {len(raw_games)} games")
    print()

    # Step 3: Transform to final JSON format
    print("[3/4] Transforming to JSON format...")
    try:
        schedule_data = transform_to_json_format(raw_games)
    except Exception as e:
        print(f"ERROR: Failed to transform data: {e}")
        return 1

    print(f"      Transformed {schedule_data['count']} games")
    print(f"      Updated timestamp: {schedule_data['updated']}")
    print()

    # Step 4: Write to data/schedule.json
    print("[4/4] Writing to data/schedule.json...")
    output_path = Path(__file__).parent / 'data' / 'schedule.json'

    try:
        # Ensure data directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON with pretty printing
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=2)

        print(f"      Successfully wrote to {output_path}")
        print()
    except Exception as e:
        print(f"ERROR: Failed to write file: {e}")
        return 1

    # Success summary
    print("=" * 60)
    print("SUCCESS: Schedule update complete")
    print("=" * 60)
    print(f"Games updated: {schedule_data['count']}")
    print(f"Timestamp: {schedule_data['updated']}")
    print(f"Output file: {output_path}")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
