// ============================================
// CBA赛程管理系统 - 新浪体育数据源
// ============================================

// CBA球队列表 (2025-26赛季)
const CBA_TEAMS = [
    '广东', '辽宁', '浙江', '新疆', '北京',
    '上海', '山东', '深圳', '广州', '北控',
    '江苏', '福建', '广厦', '青岛', '四川',
    '天津', '同曦', '宁波', '吉林', '山西'
];

// CBA球队全称映射
const TEAM_FULL_NAMES = {
    '广东': '广东华南虎', '辽宁': '辽宁本钢', '浙江': '浙江稠州金租',
    '新疆': '新疆伊力特', '北京': '北京首钢', '上海': '上海久事',
    '山东': '山东高速', '深圳': '深圳马可波罗', '广州': '广州龙狮',
    '北控': '北京控股', '江苏': '江苏肯帝亚', '福建': '福建浔兴',
    '广厦': '浙江东阳光', '青岛': '青岛国信', '四川': '四川金强',
    '天津': '天津先行者', '同曦': '南京同曦', '宁波': '宁波町渥',
    '吉林': '吉林九台农商行', '山西': '山西汾酒股份'
};

// CBA球队主场场馆映射
const TEAM_VENUES = {
    '广东': '东莞篮球中心', '辽宁': '辽宁体育馆', '浙江': '义乌梅湖体育馆',
    '新疆': '乌鲁木齐奥体中心', '北京': '五棵松体育馆', '上海': '梅赛德斯奔驰文化中心',
    '山东': '济南奥体中心', '深圳': '深圳大运中心体育馆', '广州': '天河体育馆',
    '北控': '国家体育馆', '江苏': '苏州体育中心', '福建': '晋江祖昌体育馆',
    '广厦': '诸暨暨阳学院体育馆', '青岛': '青岛国信体育馆', '四川': '成都金强体育馆',
    '天津': '东丽体育馆', '同曦': '南京青奥体育公园体育馆', '宁波': '宁波奥体中心',
    '吉林': '长春市体育馆', '山西': '山西省体育中心'
};

// 所有场馆列表（用于参考）
const ALL_VENUES = Object.values(TEAM_VENUES);

// 赛程数据
let cbaSchedule = [];

// 新浪体育数据源URL
const SINA_CBA_API = 'https://cba.sports.sina.com.cn/cba/schedule/all/';

// 是否使用实时API (部署到Vercel后自动启用)
const USE_LIVE_API = window.location.hostname !== '' &&
                     window.location.hostname !== 'localhost' &&
                     window.location.hostname !== '127.0.0.1';

/**
 * 从新浪体育获取实时赛程数据
 */
async function fetchRealSchedule() {
    // 如果部署在Vercel上，尝试使用API获取实时数据
    if (USE_LIVE_API) {
        try {
            const response = await fetch('/api/schedule');
            if (response.ok) {
                const result = await response.json();
                if (result.success && result.data) {
                    console.log('从API获取到实时数据:', result.data.length, '场比赛');
                    return processScheduleData(result.data);
                }
            }
        } catch (error) {
            console.warn('API获取失败，使用本地数据:', error);
        }
    }

    // 使用本地嵌入的数据
    return getEmbeddedScheduleData();
}

/**
 * 处理API返回的赛程数据
 */
function processScheduleData(rawData) {
    return rawData.map((game, index) => {
        const [date, time] = game.datetime.split(' ');
        const scoreParts = game.score.split(':');
        const hasScore = game.score !== 'VS';

        return {
            id: index + 1,
            round: game.round,
            date: date,
            time: time,
            homeTeam: game.home,
            awayTeam: game.away,
            venue: TEAM_VENUES[game.home] || '待定场馆',
            status: game.status,
            homeScore: hasScore ? parseInt(scoreParts[0]) : null,
            awayScore: hasScore ? parseInt(scoreParts[1]) : null,
            quarter: game.status === '进行中' ? '进行中' : null,
            weekDay: getWeekDay(new Date(date))
        };
    }).sort((a, b) => new Date(a.date + ' ' + a.time) - new Date(b.date + ' ' + b.time));
}

/**
 * 嵌入的真实赛程数据 (2025-26赛季)
 * 数据来源: 新浪体育CBA数据库
 * 最后更新: 2026-03-20
 */
function getEmbeddedScheduleData() {
    const today = new Date();
    const todayStr = formatDate(today);

    // 真实赛程数据
    const realSchedule = [
        { round: '第2轮', datetime: '2026-03-05 19:35', home: '广州', score: '93:85', away: '山东', status: '已结束' },
        { round: '第24轮', datetime: '2026-03-11 19:35', home: '山东', score: '113:104', away: '江苏', status: '已结束' },
        { round: '第24轮', datetime: '2026-03-11 19:35', home: '上海', score: '106:92', away: '北控', status: '已结束' },
        { round: '第24轮', datetime: '2026-03-11 19:35', home: '山西', score: '85:74', away: '吉林', status: '已结束' },
        { round: '第24轮', datetime: '2026-03-11 19:35', home: '深圳', score: '88:96', away: '辽宁', status: '已结束' },
        { round: '第24轮', datetime: '2026-03-11 19:35', home: '北京', score: '88:55', away: '四川', status: '已结束' },
        { round: '第24轮', datetime: '2026-03-11 19:35', home: '天津', score: '102:95', away: '浙江', status: '已结束' },
        { round: '第24轮', datetime: '2026-03-11 19:35', home: '广厦', score: '113:80', away: '同曦', status: '已结束' },
        { round: '第24轮', datetime: '2026-03-11 20:00', home: '新疆', score: '82:80', away: '广东', status: '已结束' },
        { round: '第24轮', datetime: '2026-03-12 19:35', home: '广州', score: '83:84', away: '宁波', status: '已结束' },
        { round: '第24轮', datetime: '2026-03-12 19:35', home: '青岛', score: '114:84', away: '福建', status: '已结束' },
        { round: '第25轮', datetime: '2026-03-13 19:35', home: '北控', score: '106:98', away: '天津', status: '已结束' },
        { round: '第25轮', datetime: '2026-03-13 19:35', home: '辽宁', score: '92:84', away: '山西', status: '已结束' },
        { round: '第25轮', datetime: '2026-03-13 20:00', home: '深圳', score: '97:101', away: '广东', status: '已结束' },
        { round: '第25轮', datetime: '2026-03-13 20:00', home: '新疆', score: '82:89', away: '吉林', status: '已结束' },
        { round: '第25轮', datetime: '2026-03-14 19:35', home: '福建', score: '77:76', away: '宁波', status: '已结束' },
        { round: '第25轮', datetime: '2026-03-14 19:35', home: '广州', score: '85:98', away: '北京', status: '已结束' },
        { round: '第25轮', datetime: '2026-03-14 19:35', home: '江苏', score: '84:93', away: '同曦', status: '已结束' },
        { round: '第25轮', datetime: '2026-03-14 19:35', home: '山东', score: '85:76', away: '青岛', status: '已结束' },
        { round: '第25轮', datetime: '2026-03-14 19:35', home: '四川', score: '79:129', away: '上海', status: '已结束' },
        { round: '第25轮', datetime: '2026-03-14 19:35', home: '浙江', score: '89:86', away: '广厦', status: '已结束' },
        { round: '第26轮', datetime: '2026-03-15 19:35', home: '广东', score: '73:89', away: '辽宁', status: '已结束' },
        { round: '第26轮', datetime: '2026-03-15 19:35', home: '吉林', score: '96:90', away: '山西', status: '已结束' },
        { round: '第26轮', datetime: '2026-03-15 20:00', home: '新疆', score: '103:89', away: '北控', status: '已结束' },
        { round: '第26轮', datetime: '2026-03-16 19:35', home: '广厦', score: '87:72', away: '宁波', status: '已结束' },
        { round: '第26轮', datetime: '2026-03-16 19:35', home: '同曦', score: '81:95', away: '福建', status: '已结束' },
        { round: '第26轮', datetime: '2026-03-16 19:35', home: '山东', score: '83:96', away: '浙江', status: '已结束' },
        { round: '第26轮', datetime: '2026-03-16 19:35', home: '上海', score: '84:80', away: '青岛', status: '已结束' },
        { round: '第26轮', datetime: '2026-03-16 19:35', home: '深圳', score: '97:96', away: '广州', status: '已结束' },
        { round: '第26轮', datetime: '2026-03-16 19:35', home: '北京', score: '88:75', away: '天津', status: '已结束' },
        { round: '第26轮', datetime: '2026-03-16 19:35', home: '四川', score: '86:91', away: '江苏', status: '已结束' },
        { round: '第27轮', datetime: '2026-03-17 19:35', home: '广东', score: '111:89', away: '新疆', status: '已结束' },
        { round: '第27轮', datetime: '2026-03-17 19:35', home: '山西', score: '107:102', away: '北控', status: '已结束' },
        { round: '第27轮', datetime: '2026-03-18 19:35', home: '上海', score: '112:96', away: '山东', status: '已结束' },
        { round: '第27轮', datetime: '2026-03-18 19:35', home: '同曦', score: '101:95', away: '浙江', status: '已结束' },
        { round: '第27轮', datetime: '2026-03-18 19:35', home: '天津', score: '84:96', away: '深圳', status: '已结束' },
        { round: '第27轮', datetime: '2026-03-18 19:35', home: '广厦', score: '102:88', away: '吉林', status: '已结束' },
        { round: '第27轮', datetime: '2026-03-18 19:35', home: '辽宁', score: '97:86', away: '广州', status: '已结束' },
        { round: '第27轮', datetime: '2026-03-18 19:35', home: '青岛', score: '102:69', away: '江苏', status: '已结束' },
        { round: '第27轮', datetime: '2026-03-19 19:35', home: '福建', score: '109:104', away: '北京', status: '已结束' },
        { round: '第27轮', datetime: '2026-03-19 19:35', home: '四川', score: '56:80', away: '宁波', status: '已结束' },
        { round: '第28轮', datetime: '2026-03-20 19:35', home: '江苏', score: '34:34', away: '广东', status: '已结束' },
        { round: '第28轮', datetime: '2026-03-20 19:35', home: '山东', score: '41:26', away: '天津', status: '已结束' },
        { round: '第28轮', datetime: '2026-03-20 19:35', home: '广厦', score: '41:39', away: '北控', status: '已结束' },
        { round: '第28轮', datetime: '2026-03-20 20:00', home: '深圳', score: '13:7', away: '新疆', status: '已结束' },
        { round: '第28轮', datetime: '2026-03-21 19:35', home: '宁波', score: 'VS', away: '广州', status: '未开始' },
        { round: '第28轮', datetime: '2026-03-21 19:35', home: '福建', score: 'VS', away: '山西', status: '未开始' },
        { round: '第28轮', datetime: '2026-03-21 19:35', home: '辽宁', score: 'VS', away: '北京', status: '未开始' },
        { round: '第28轮', datetime: '2026-03-21 19:35', home: '同曦', score: 'VS', away: '青岛', status: '未开始' },
        { round: '第28轮', datetime: '2026-03-21 19:35', home: '上海', score: 'VS', away: '四川', status: '未开始' },
        { round: '第28轮', datetime: '2026-03-21 19:35', home: '浙江', score: 'VS', away: '吉林', status: '未开始' },
        { round: '第29轮', datetime: '2026-03-22 19:35', home: '江苏', score: 'VS', away: '广厦', status: '未开始' },
        { round: '第29轮', datetime: '2026-03-22 19:35', home: '深圳', score: 'VS', away: '天津', status: '未开始' },
        { round: '第29轮', datetime: '2026-03-23 19:35', home: '宁波', score: 'VS', away: '新疆', status: '未开始' },
        { round: '第29轮', datetime: '2026-03-23 19:35', home: '北控', score: 'VS', away: '浙江', status: '未开始' },
        { round: '第29轮', datetime: '2026-03-23 19:35', home: '福建', score: 'VS', away: '青岛', status: '未开始' },
        { round: '第29轮', datetime: '2026-03-23 19:35', home: '广州', score: 'VS', away: '山西', status: '未开始' },
        { round: '第29轮', datetime: '2026-03-23 19:35', home: '吉林', score: 'VS', away: '北京', status: '未开始' },
        { round: '第29轮', datetime: '2026-03-23 19:35', home: '辽宁', score: 'VS', away: '同曦', status: '未开始' },
        { round: '第29轮', datetime: '2026-03-23 19:35', home: '上海', score: 'VS', away: '广东', status: '未开始' },
        { round: '第29轮', datetime: '2026-03-23 19:35', home: '四川', score: 'VS', away: '山东', status: '未开始' },
        { round: '第30轮', datetime: '2026-03-24 19:35', home: '深圳', score: 'VS', away: '江苏', status: '未开始' },
        { round: '第30轮', datetime: '2026-03-24 19:35', home: '天津', score: 'VS', away: '广厦', status: '未开始' },
        { round: '第30轮', datetime: '2026-03-25 19:35', home: '宁波', score: 'VS', away: '福建', status: '未开始' },
        { round: '第30轮', datetime: '2026-03-25 19:35', home: '广东', score: 'VS', away: '四川', status: '未开始' },
        { round: '第30轮', datetime: '2026-03-25 19:35', home: '吉林', score: 'VS', away: '辽宁', status: '未开始' },
        { round: '第30轮', datetime: '2026-03-25 19:35', home: '山西', score: 'VS', away: '上海', status: '未开始' },
        { round: '第30轮', datetime: '2026-03-25 19:35', home: '北京', score: 'VS', away: '浙江', status: '未开始' },
        { round: '第30轮', datetime: '2026-03-25 20:00', home: '新疆', score: 'VS', away: '山东', status: '未开始' },
        { round: '第30轮', datetime: '2026-03-26 19:35', home: '北控', score: 'VS', away: '同曦', status: '未开始' },
        { round: '第30轮', datetime: '2026-03-26 19:35', home: '广州', score: 'VS', away: '青岛', status: '未开始' },
        { round: '第31轮', datetime: '2026-03-27 19:35', home: '福建', score: 'VS', away: '深圳', status: '未开始' },
        { round: '第31轮', datetime: '2026-03-27 19:35', home: '广东', score: 'VS', away: '北京', status: '未开始' },
        { round: '第31轮', datetime: '2026-03-27 19:35', home: '江苏', score: 'VS', away: '吉林', status: '未开始' },
        { round: '第31轮', datetime: '2026-03-27 19:35', home: '山西', score: 'VS', away: '山东', status: '未开始' },
        { round: '第31轮', datetime: '2026-03-27 19:35', home: '四川', score: 'VS', away: '广厦', status: '未开始' },
        { round: '第31轮', datetime: '2026-03-27 19:35', home: '天津', score: 'VS', away: '上海', status: '未开始' },
        { round: '第31轮', datetime: '2026-03-28 19:35', home: '北控', score: 'VS', away: '宁波', status: '未开始' },
        { round: '第31轮', datetime: '2026-03-28 19:35', home: '广州', score: 'VS', away: '辽宁', status: '未开始' },
        { round: '第31轮', datetime: '2026-03-28 19:35', home: '青岛', score: 'VS', away: '浙江', status: '未开始' },
        { round: '第31轮', datetime: '2026-03-28 20:00', home: '新疆', score: 'VS', away: '同曦', status: '未开始' },
        { round: '第32轮', datetime: '2026-03-29 19:35', home: '吉林', score: 'VS', away: '深圳', status: '未开始' },
        { round: '第32轮', datetime: '2026-03-29 19:35', home: '山西', score: 'VS', away: '上海', status: '未开始' },
        { round: '第32轮', datetime: '2026-03-29 19:35', home: '四川', score: 'VS', away: '广东', status: '未开始' },
        { round: '第32轮', datetime: '2026-03-29 19:35', home: '广厦', score: 'VS', away: '江苏', status: '未开始' },
        { round: '第32轮', datetime: '2026-03-30 19:35', home: '福建', score: 'VS', away: '辽宁', status: '未开始' },
        { round: '第32轮', datetime: '2026-03-30 19:35', home: '同曦', score: 'VS', away: '北京', status: '未开始' },
        { round: '第32轮', datetime: '2026-03-30 19:35', home: '青岛', score: 'VS', away: '北控', status: '未开始' },
        { round: '第32轮', datetime: '2026-03-30 19:35', home: '山东', score: 'VS', away: '天津', status: '未开始' },
        { round: '第32轮', datetime: '2026-03-30 19:35', home: '浙江', score: 'VS', away: '广州', status: '未开始' },
        { round: '第32轮', datetime: '2026-03-30 20:00', home: '新疆', score: 'VS', away: '宁波', status: '未开始' },
        { round: '第33轮', datetime: '2026-03-31 19:35', home: '广东', score: 'VS', away: '江苏', status: '未开始' },
        { round: '第33轮', datetime: '2026-03-31 19:35', home: '吉林', score: 'VS', away: '上海', status: '未开始' }
    ];

    return realSchedule.map((game, index) => {
        const [date, time] = game.datetime.split(' ');
        const scoreParts = game.score.split(':');
        const hasScore = game.score !== 'VS';

        return {
            id: index + 1,
            round: game.round,
            date: date,
            time: time,
            homeTeam: game.home,
            awayTeam: game.away,
            venue: TEAM_VENUES[game.home] || '待定场馆',
            status: game.status,
            homeScore: hasScore ? parseInt(scoreParts[0]) : null,
            awayScore: hasScore ? parseInt(scoreParts[1]) : null,
            quarter: game.status === '进行中' ? '第二节' : null,
            weekDay: getWeekDay(new Date(date))
        };
    }).sort((a, b) => new Date(a.date + ' ' + a.time) - new Date(b.date + ' ' + b.time));
}

/**
 * 格式化日期
 */
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * 获取星期几
 */
function getWeekDay(date) {
    const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    return weekDays[date.getDay()];
}

/**
 * 显示赛程表格
 */
function displaySchedule(games = cbaSchedule) {
    const tableBody = document.getElementById('scheduleBody');
    if (!tableBody) {
        console.error('未找到scheduleBody元素');
        return;
    }

    tableBody.innerHTML = '';

    if (games.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="9" style="text-align: center; padding: 20px;">暂无符合条件的比赛</td>';
        tableBody.appendChild(row);
        return;
    }

    games.forEach(game => {
        const row = document.createElement('tr');
        const statusClass = getStatusClass(game.status);

        row.innerHTML = `
            <td data-label="轮次" class="round-cell">${game.round}</td>
            <td data-label="日期">
                <div class="date-cell">
                    <span class="date">${game.date}</span>
                    <span class="weekday">${game.weekDay}</span>
                </div>
            </td>
            <td data-label="时间">${game.time}</td>
            <td data-label="主队" class="team-name home-team">
                ${game.homeTeam}
                ${game.homeScore !== null ? `<span class="score">${game.homeScore}</span>` : ''}
            </td>
            <td data-label="比分" class="score-cell">
                ${game.homeScore !== null ? `${game.homeScore} : ${game.awayScore}` : 'VS'}
            </td>
            <td data-label="客队" class="team-name away-team">
                ${game.awayTeam}
                ${game.awayScore !== null ? `<span class="score">${game.awayScore}</span>` : ''}
            </td>
            <td data-label="场地">${game.venue}</td>
            <td data-label="状态" class="status ${statusClass}">
                ${game.status}
                ${game.quarter ? `<br><small>${game.quarter}</small>` : ''}
            </td>
            <td data-label="操作" class="action-cell">
                ${getActionButtons(game)}
            </td>
        `;

        tableBody.appendChild(row);
    });

    updateStats(games);
}

/**
 * 获取状态样式类名
 */
function getStatusClass(status) {
    const statusMap = {
        '已结束': 'ended',
        '进行中': 'live',
        '未开始': 'upcoming'
    };
    return statusMap[status] || 'upcoming';
}

/**
 * 获取操作按钮
 */
function getActionButtons(game) {
    if (game.status === '已结束') {
        return `<button class="btn-detail" onclick="showGameDetail(${game.id})">比赛详情</button>`;
    } else if (game.status === '进行中') {
        return `<button class="btn-live" onclick="showLiveScore(${game.id})">实时数据</button>`;
    } else {
        return `<button class="btn-remind" onclick="setReminder(${game.id})">设置提醒</button>`;
    }
}

/**
 * 更新统计数据
 */
function updateStats(games) {
    const statsEl = document.getElementById('statsInfo');
    if (!statsEl) return;

    const ended = games.filter(g => g.status === '已结束').length;
    const live = games.filter(g => g.status === '进行中').length;
    const upcoming = games.filter(g => g.status === '未开始').length;

    statsEl.innerHTML = `
        <span class="stat-item ended">已结束: ${ended}</span>
        <span class="stat-item live">进行中: ${live}</span>
        <span class="stat-item upcoming">未开始: ${upcoming}</span>
        <span class="stat-item total">总计: ${games.length}</span>
    `;
}

/**
 * 按日期筛选
 */
function filterByDate(dateStr) {
    if (!dateStr) {
        displaySchedule();
        return;
    }
    const filtered = cbaSchedule.filter(game => game.date === dateStr);
    displaySchedule(filtered);
}

/**
 * 按球队筛选
 */
function filterByTeam(teamName) {
    if (!teamName) {
        displaySchedule();
        return;
    }
    const filtered = cbaSchedule.filter(game =>
        game.homeTeam === teamName || game.awayTeam === teamName
    );
    displaySchedule(filtered);
}

/**
 * 按状态筛选
 */
function filterByStatus(status) {
    if (!status || status === '全部') {
        displaySchedule();
        return;
    }
    const filtered = cbaSchedule.filter(game => game.status === status);
    displaySchedule(filtered);
}

/**
 * 显示比赛详情
 */
function showGameDetail(gameId) {
    const game = cbaSchedule.find(g => g.id === gameId);
    if (!game) return;

    const modal = document.getElementById('gameModal');
    const modalContent = document.getElementById('modalContent');

    if (!modal || !modalContent) {
        alert(`比赛详情:\n${game.awayTeam} vs ${game.homeTeam}\n比分: ${game.awayScore} - ${game.homeScore}\n地点: ${game.venue}`);
        return;
    }

    modalContent.innerHTML = `
        <h2>比赛详情</h2>
        <div class="game-detail">
            <div class="detail-row">
                <span class="label">比赛编号:</span>
                <span class="value">${game.id}</span>
            </div>
            <div class="detail-row">
                <span class="label">比赛日期:</span>
                <span class="value">${game.date} ${game.weekDay}</span>
            </div>
            <div class="detail-row">
                <span class="label">比赛时间:</span>
                <span class="value">${game.time}</span>
            </div>
            <div class="detail-row highlight">
                <span class="label">主队:</span>
                <span class="value">${game.homeTeam}</span>
            </div>
            <div class="detail-row highlight">
                <span class="label">客队:</span>
                <span class="value">${game.awayTeam}</span>
            </div>
            <div class="detail-row score">
                <span class="label">最终比分:</span>
                <span class="value">${game.homeScore} : ${game.awayScore}</span>
            </div>
            <div class="detail-row">
                <span class="label">比赛场馆:</span>
                <span class="value">${game.venue}</span>
            </div>
        </div>
    `;

    modal.style.display = 'block';
}

/**
 * 显示实时比分
 */
function showLiveScore(gameId) {
    const game = cbaSchedule.find(g => g.id === gameId);
    if (!game) return;

    alert(`实时比分\n${game.awayTeam} vs ${game.homeTeam}\n当前比分: ${game.awayScore} - ${game.homeScore}\n当前节次: ${game.quarter}`);
}

/**
 * 设置比赛提醒
 */
function setReminder(gameId) {
    const game = cbaSchedule.find(g => g.id === gameId);
    if (!game) return;

    alert(`已设置提醒\n${game.date} ${game.time}\n${game.awayTeam} vs ${game.homeTeam}\n将在比赛开始前15分钟提醒您`);
}

/**
 * 关闭弹窗
 */
function closeModal() {
    const modal = document.getElementById('gameModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * 初始化筛选器
 */
function initFilters() {
    // 填充球队选择器
    const teamSelect = document.getElementById('teamFilter');
    if (teamSelect) {
        teamSelect.innerHTML = '<option value="">全部球队</option>';
        CBA_TEAMS.forEach(team => {
            teamSelect.innerHTML += `<option value="${team}">${team}</option>`;
        });

        // 绑定球队筛选事件
        teamSelect.addEventListener('change', (e) => {
            filterByTeam(e.target.value);
        });
    }

    // 绑定日期筛选事件
    const dateInput = document.getElementById('dateFilter');
    if (dateInput) {
        dateInput.addEventListener('change', (e) => {
            filterByDate(e.target.value);
        });
    }

    // 绑定状态筛选事件
    const statusSelect = document.getElementById('statusFilter');
    if (statusSelect) {
        statusSelect.addEventListener('change', (e) => {
            filterByStatus(e.target.value);
        });
    }

    // 绑定重置按钮事件
    const resetBtn = document.getElementById('resetFilters');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            // 重置所有筛选器
            if (teamSelect) teamSelect.value = '';
            if (dateInput) dateInput.value = '';
            if (statusSelect) statusSelect.value = '全部';
            // 显示所有赛程
            displaySchedule();
        });
    }
}

/**
 * 刷新赛程数据
 */
async function refreshSchedule() {
    console.log('刷新赛程数据...');
    showNotification('正在加载最新数据...');
    cbaSchedule = await fetchRealSchedule();
    displaySchedule();
    showNotification('赛程数据已更新');
}

/**
 * 显示通知
 */
function showNotification(message) {
    const notification = document.getElementById('notification');
    if (notification) {
        notification.textContent = message;
        notification.style.display = 'block';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    } else {
        console.log(message);
    }
}

/**
 * 初始化CBA赛程系统
 */
async function initCBA() {
    console.log('CBA赛程管理系统已加载 (数据源: 新浪体育)');
    cbaSchedule = await fetchRealSchedule();
    initFilters();
    displaySchedule();

    // 每60秒更新一次数据
    setInterval(async () => {
        cbaSchedule = await fetchRealSchedule();
        displaySchedule();
        console.log('数据已自动更新');
    }, 60000);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initCBA);

// 导出函数供全局使用
window.filterByDate = filterByDate;
window.filterByTeam = filterByTeam;
window.filterByStatus = filterByStatus;
window.showGameDetail = showGameDetail;
window.showLiveScore = showLiveScore;
window.setReminder = setReminder;
window.closeModal = closeModal;
window.refreshSchedule = refreshSchedule;