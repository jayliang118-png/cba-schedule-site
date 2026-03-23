"""
CBA Schedule Flask Application
Serves HTML pages and JSON API endpoints from single codebase
"""

from flask import Flask, render_template, jsonify, request, make_response

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
    """Homepage route - renders schedule template with sample data"""
    # Sample schedule data (will be replaced with real data in Phase 2)
    sample_schedule = [
        {
            'id': 1,
            'round': '第1轮',
            'date': '2025-10-20',
            'time': '19:35',
            'homeTeam': '广东',
            'awayTeam': '辽宁',
            'venue': '东莞篮球中心',
            'status': '未开始',
            'homeScore': None,
            'awayScore': None,
            'weekDay': '周一'
        },
        {
            'id': 2,
            'round': '第1轮',
            'date': '2025-10-20',
            'time': '19:35',
            'homeTeam': '浙江',
            'awayTeam': '新疆',
            'venue': '义乌梅湖体育馆',
            'status': '进行中',
            'homeScore': 45,
            'awayScore': 42,
            'weekDay': '周一'
        },
        {
            'id': 3,
            'round': '第1轮',
            'date': '2025-10-19',
            'time': '19:35',
            'homeTeam': '北京',
            'awayTeam': '上海',
            'venue': '五棵松体育馆',
            'status': '已结束',
            'homeScore': 98,
            'awayScore': 92,
            'weekDay': '周日'
        }
    ]

    return render_template('schedule.html', schedule=sample_schedule, teams=CBA_TEAMS)

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
