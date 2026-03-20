// ============================================
// CBA赛程管理系统 - 模拟数据与显示功能
// ============================================

// CBA球队列表
const CBA_TEAMS = [
    '广东华南虎', '辽宁本钢', '浙江东阳光', '新疆伊力特',
    '北京北汽', '上海久事', '山东高速', '深圳马可波罗',
    '广州龙狮', '北京控股', '江苏肯帝亚', '福建浔兴股份',
    '浙江稠州金租', '青岛国信水产', '四川金强', '天津先行者',
    '南京头排苏酒', '宁波町渥', '吉林九台农商行', '山西汾酒股份'
];

// CBA球队主场场馆映射（真实主场）
const TEAM_VENUES = {
    '广东华南虎': '东莞篮球中心',
    '辽宁本钢': '辽宁体育馆',
    '浙江东阳光': '诸暨暨阳学院体育馆',
    '新疆伊力特': '乌鲁木齐奥体中心',
    '北京北汽': '五棵松体育馆',
    '上海久事': '梅赛德斯奔驰文化中心',
    '山东高速': '济南奥体中心',
    '深圳马可波罗': '深圳大运中心体育馆',
    '广州龙狮': '天河体育馆',
    '北京控股': '国家体育馆',
    '江苏肯帝亚': '苏州体育中心',
    '福建浔兴股份': '晋江祖昌体育馆',
    '浙江稠州金租': '义乌梅湖体育馆',
    '青岛国信水产': '青岛国信体育馆',
    '四川金强': '成都金强体育馆',
    '天津先行者': '东丽体育馆',
    '南京头排苏酒': '南京青奥体育公园体育馆',
    '宁波町渥': '宁波奥体中心',
    '吉林九台农商行': '长春市体育馆',
    '山西汾酒股份': '山西省体育中心'
};

// 所有场馆列表（用于参考）
const ALL_VENUES = Object.values(TEAM_VENUES);

// 模拟赛程数据
let cbaSchedule = [];

/**
 * 生成模拟比赛数据
 */
function generateMockSchedule() {
    const schedule = [];
    const today = new Date();
    let gameId = 1;

    // 生成过去3天的比赛（已结束）
    for (let i = 3; i >= 1; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const gamesPerDay = Math.floor(Math.random() * 3) + 2;

        for (let j = 0; j < gamesPerDay; j++) {
            const homeTeam = CBA_TEAMS[Math.floor(Math.random() * CBA_TEAMS.length)];
            let awayTeam = CBA_TEAMS[Math.floor(Math.random() * CBA_TEAMS.length)];
            while (awayTeam === homeTeam) {
                awayTeam = CBA_TEAMS[Math.floor(Math.random() * CBA_TEAMS.length)];
            }

            schedule.push(createGame(gameId++, date, homeTeam, awayTeam, '已结束'));
        }
    }

    // 今天的比赛（部分进行中，部分未开始）
    const todayGames = Math.floor(Math.random() * 3) + 3;
    for (let j = 0; j < todayGames; j++) {
        const homeTeam = CBA_TEAMS[Math.floor(Math.random() * CBA_TEAMS.length)];
        let awayTeam = CBA_TEAMS[Math.floor(Math.random() * CBA_TEAMS.length)];
        while (awayTeam === homeTeam) {
            awayTeam = CBA_TEAMS[Math.floor(Math.random() * CBA_TEAMS.length)];
        }

        // 前两场比赛进行中，其余未开始
        const status = j < 2 ? '进行中' : '未开始';
        schedule.push(createGame(gameId++, today, homeTeam, awayTeam, status));
    }

    // 未来7天的比赛（未开始）
    for (let i = 1; i <= 7; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() + i);
        const gamesPerDay = Math.floor(Math.random() * 4) + 2;

        for (let j = 0; j < gamesPerDay; j++) {
            const homeTeam = CBA_TEAMS[Math.floor(Math.random() * CBA_TEAMS.length)];
            let awayTeam = CBA_TEAMS[Math.floor(Math.random() * CBA_TEAMS.length)];
            while (awayTeam === homeTeam) {
                awayTeam = CBA_TEAMS[Math.floor(Math.random() * CBA_TEAMS.length)];
            }

            schedule.push(createGame(gameId++, date, homeTeam, awayTeam, '未开始'));
        }
    }

    return schedule.sort((a, b) => new Date(a.date) - new Date(b.date));
}

/**
 * 创建单场比赛数据
 */
function createGame(id, date, homeTeam, awayTeam, status) {
    const gameDate = formatDate(date);
    // CBA标准比赛时间：19:35（黄金时段）和15:00（下午场）
    // 晚场比赛占比约70%，下午场占比约30%
    const gameTime = Math.random() < 0.7 ? '19:35' : '15:00';

    const game = {
        id,
        date: gameDate,
        time: gameTime,
        homeTeam,
        awayTeam,
        venue: TEAM_VENUES[homeTeam] || '待定场馆',
        status,
        homeScore: null,
        awayScore: null,
        quarter: null,
        weekDay: getWeekDay(date)
    };

    // 为已结束的比赛生成分数
    if (status === '已结束') {
        game.homeScore = Math.floor(Math.random() * 40) + 80;
        game.awayScore = Math.floor(Math.random() * 40) + 80;
        // 确保不会平局
        if (game.homeScore === game.awayScore) {
            game.homeScore += 1;
        }
    }

    // 为进行中的比赛生成当前比分和节次
    if (status === '进行中') {
        game.homeScore = Math.floor(Math.random() * 30) + 60;
        game.awayScore = Math.floor(Math.random() * 30) + 60;
        game.quarter = ['第一节', '第二节', '第三节', '第四节'][Math.floor(Math.random() * 4)];
    }

    return game;
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
        row.innerHTML = '<td colspan="8" style="text-align: center; padding: 20px;">暂无符合条件的比赛</td>';
        tableBody.appendChild(row);
        return;
    }

    games.forEach(game => {
        const row = document.createElement('tr');
        const statusClass = getStatusClass(game.status);

        row.innerHTML = `
            <td data-label="序号">${game.id}</td>
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
        game.homeTeam.includes(teamName) || game.awayTeam.includes(teamName)
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
function refreshSchedule() {
    console.log('刷新赛程数据...');
    cbaSchedule = generateMockSchedule();
    displaySchedule();
    showNotification('赛程数据已刷新');
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
 * 模拟实时更新（用于演示）
 */
function simulateLiveUpdate() {
    const liveGames = cbaSchedule.filter(g => g.status === '进行中');

    liveGames.forEach(game => {
        // 随机增加分数
        if (Math.random() > 0.5) {
            game.homeScore += Math.floor(Math.random() * 3);
        } else {
            game.awayScore += Math.floor(Math.random() * 3);
        }
    });

    if (liveGames.length > 0) {
        displaySchedule();
        console.log('实时数据已更新');
    }
}

/**
 * 初始化CBA赛程系统
 */
function initCBA() {
    console.log('CBA赛程管理系统已加载');
    cbaSchedule = generateMockSchedule();
    initFilters();
    displaySchedule();

    // 每30秒模拟一次实时更新
    setInterval(simulateLiveUpdate, 30000);
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