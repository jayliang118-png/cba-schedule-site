"""
CBA Schedule Flask Application
Serves HTML pages and JSON API endpoints from single codebase
"""

from flask import Flask, render_template, jsonify, request, make_response
import json
from pathlib import Path
from datetime import datetime

# Flask app initialization
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# CBA球队列表 (2025-26赛季)
CBA_TEAMS = [
    '广东', '辽宁', '浙江', '新疆', '北京',
    '上海', '山东', '深圳', '广州', '北控',
    '江苏', '福建', '广厦', '青岛', '四川',
    '天津', '同曦', '宁波', '吉林', '山西'
]

# CBA球队全称映射
TEAM_FULL_NAMES = {
    '广东': '广东华南虎', '辽宁': '辽宁本钢', '浙江': '浙江稠州金租',
    '新疆': '新疆伊力特', '北京': '北京首钢', '上海': '上海久事',
    '山东': '山东高速', '深圳': '深圳马可波罗', '广州': '广州龙狮',
    '北控': '北京控股', '江苏': '江苏肯帝亚', '福建': '福建浔兴',
    '广厦': '浙江东阳光', '青岛': '青岛国信', '四川': '四川金强',
    '天津': '天津先行者', '同曦': '南京同曦', '宁波': '宁波町渥',
    '吉林': '吉林九台农商行', '山西': '山西汾酒股份'
}

# CBA球队主场场馆映射
TEAM_VENUES = {
    '广东': '东莞篮球中心', '辽宁': '辽宁体育馆', '浙江': '义乌梅湖体育馆',
    '新疆': '乌鲁木齐奥体中心', '北京': '五棵松体育馆', '上海': '梅赛德斯奔驰文化中心',
    '山东': '济南奥体中心', '深圳': '深圳大运中心体育馆', '广州': '天河体育馆',
    '北控': '国家体育馆', '江苏': '苏州体育中心', '福建': '晋江祖昌体育馆',
    '广厦': '诸暨暨阳学院体育馆', '青岛': '青岛国信体育馆', '四川': '成都金强体育馆',
    '天津': '东丽体育馆', '同曦': '南京青奥体育公园体育馆', '宁波': '宁波奥体中心',
    '吉林': '长春市体育馆', '山西': '山西省体育中心'
}


def load_schedule_data():
    """Load schedule from embedded JSON file"""
    schedule_path = Path(__file__).parent / 'data' / 'schedule.json'
    try:
        with open(schedule_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['schedule']
    except FileNotFoundError:
        print(f"Warning: schedule.json not found at {schedule_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing schedule.json: {e}")
        return []


# Load schedule on module import (cached)
SCHEDULE_DATA = load_schedule_data()

# CORS headers for API endpoints
@app.after_request
def add_cors_headers(response):
    """Add CORS headers to allow cross-origin API requests"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Routes
@app.route('/')
def index():
    """Homepage route - renders schedule template with real data"""
    return render_template('schedule.html', schedule=SCHEDULE_DATA, teams=CBA_TEAMS)


@app.route('/api/schedule')
def api_schedule():
    """
    API endpoint returning CBA schedule as JSON (DATA-04)

    Response format:
    {
        "success": true,
        "data": [...schedule array...],
        "count": 100,
        "updated": "2026-03-23T10:30:00Z"
    }
    """
    try:
        # Read schedule.json to get updated timestamp
        schedule_path = Path(__file__).parent / 'data' / 'schedule.json'
        with open(schedule_path, 'r', encoding='utf-8') as f:
            full_data = json.load(f)

        return jsonify({
            'success': True,
            'data': SCHEDULE_DATA,
            'count': len(SCHEDULE_DATA),
            'updated': full_data.get('updated', datetime.utcnow().isoformat() + 'Z')
        })
    except Exception as e:
        # Error response
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found on this server.'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An internal error occurred. Please try again later.'
    }), 500

# WSGI application export for Vercel
if __name__ == '__main__':
    app.run(debug=True)
