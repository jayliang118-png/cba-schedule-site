/**
 * CBA Schedule Filter JavaScript
 * Client-side filter interactions for schedule display
 */

/**
 * Fetch schedule data from API with optional filters
 * @param {Object} filters - Filter parameters (date, team, status)
 * @returns {Promise<Array>} Array of game objects
 */
async function fetchSchedule(filters = {}) {
    const params = new URLSearchParams();

    if (filters.date) params.append('date', filters.date);
    if (filters.team) params.append('team', filters.team);
    if (filters.status) params.append('status', filters.status);

    const queryString = params.toString();
    const url = queryString ? `/api/schedule?${queryString}` : '/api/schedule';

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            return data.data || [];
        } else {
            return [];
        }
    } catch (error) {
        return [];
    }
}

/**
 * Render schedule games in table
 * @param {Array} games - Array of game objects to render
 */
function renderSchedule(games) {
    const tbody = document.getElementById('scheduleBody');
    tbody.innerHTML = '';

    if (games.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="9" style="text-align: center; padding: 20px;">未找到比赛记录</td>';
        tbody.appendChild(emptyRow);
        return;
    }

    games.forEach(game => {
        const row = document.createElement('tr');

        // Round cell
        const roundCell = document.createElement('td');
        roundCell.setAttribute('data-label', '轮次');
        roundCell.className = 'round-cell';
        roundCell.textContent = game.round || '';
        row.appendChild(roundCell);

        // Date cell with weekDay
        const dateCell = document.createElement('td');
        dateCell.setAttribute('data-label', '日期');
        dateCell.className = 'date-cell';
        dateCell.textContent = game.date;
        if (game.weekDay) {
            const weekdaySpan = document.createElement('span');
            weekdaySpan.className = 'weekday';
            weekdaySpan.textContent = game.weekDay;
            dateCell.appendChild(document.createTextNode(' '));
            dateCell.appendChild(weekdaySpan);
        }
        row.appendChild(dateCell);

        // Time cell
        const timeCell = document.createElement('td');
        timeCell.setAttribute('data-label', '时间');
        timeCell.textContent = game.time;
        row.appendChild(timeCell);

        // Home team cell
        const homeTeamCell = document.createElement('td');
        homeTeamCell.setAttribute('data-label', '主队');
        homeTeamCell.className = 'team-name';
        homeTeamCell.textContent = game.homeTeam;
        if (game.homeScore !== null && game.homeScore !== undefined) {
            const scoreSpan = document.createElement('span');
            scoreSpan.className = 'score';
            scoreSpan.textContent = game.homeScore;
            homeTeamCell.appendChild(document.createTextNode(' '));
            homeTeamCell.appendChild(scoreSpan);
        }
        row.appendChild(homeTeamCell);

        // Score cell
        const scoreCell = document.createElement('td');
        scoreCell.setAttribute('data-label', '比分');
        scoreCell.className = 'score-cell';
        if (game.homeScore !== null && game.homeScore !== undefined &&
            game.awayScore !== null && game.awayScore !== undefined) {
            scoreCell.textContent = `${game.homeScore} : ${game.awayScore}`;
        } else {
            scoreCell.textContent = 'VS';
        }
        row.appendChild(scoreCell);

        // Away team cell
        const awayTeamCell = document.createElement('td');
        awayTeamCell.setAttribute('data-label', '客队');
        awayTeamCell.className = 'team-name';
        awayTeamCell.textContent = game.awayTeam;
        if (game.awayScore !== null && game.awayScore !== undefined) {
            const scoreSpan = document.createElement('span');
            scoreSpan.className = 'score';
            scoreSpan.textContent = game.awayScore;
            awayTeamCell.appendChild(document.createTextNode(' '));
            awayTeamCell.appendChild(scoreSpan);
        }
        row.appendChild(awayTeamCell);

        // Venue cell
        const venueCell = document.createElement('td');
        venueCell.setAttribute('data-label', '场地');
        venueCell.textContent = game.venue;
        row.appendChild(venueCell);

        // Status cell
        const statusCell = document.createElement('td');
        statusCell.setAttribute('data-label', '状态');
        statusCell.className = 'status';
        if (game.status === '已结束') {
            statusCell.classList.add('ended');
        } else if (game.status === '进行中') {
            statusCell.classList.add('live');
        } else {
            statusCell.classList.add('upcoming');
        }
        statusCell.textContent = game.status;
        row.appendChild(statusCell);

        // Action cell
        const actionCell = document.createElement('td');
        actionCell.setAttribute('data-label', '操作');
        actionCell.className = 'action-cell';
        const button = document.createElement('button');
        if (game.status === '进行中') {
            button.className = 'btn-live';
            button.textContent = '直播';
        } else if (game.status === '未开始') {
            button.className = 'btn-remind';
            button.textContent = '提醒';
        } else {
            button.className = 'btn-detail';
            button.textContent = '详情';
        }
        actionCell.appendChild(button);
        row.appendChild(actionCell);

        tbody.appendChild(row);
    });
}

/**
 * Apply current filter values and update schedule display
 */
async function applyFilters() {
    const filters = {
        date: document.getElementById('dateFilter').value,
        team: document.getElementById('teamFilter').value,
        status: document.getElementById('statusFilter').value
    };

    const games = await fetchSchedule(filters);
    renderSchedule(games);
}

document.addEventListener('DOMContentLoaded', function() {
    // Get filter element references
    const teamFilter = document.getElementById('teamFilter');
    const dateFilter = document.getElementById('dateFilter');
    const statusFilter = document.getElementById('statusFilter');
    const resetFilters = document.getElementById('resetFilters');

    // Event listeners for filter controls
    teamFilter.addEventListener('change', applyFilters);
    dateFilter.addEventListener('change', applyFilters);
    statusFilter.addEventListener('change', applyFilters);

    // Reset filters handler
    resetFilters.addEventListener('click', async function() {
        teamFilter.value = '';
        dateFilter.value = '';
        statusFilter.value = '';

        const games = await fetchSchedule({});
        renderSchedule(games);
    });

    // Load initial schedule on page load
    applyFilters();
});
