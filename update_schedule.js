/**
 * CBA赛程数据更新脚本
 * 从新浪体育获取最新赛程数据并更新到 cba_script.js
 *
 * 使用方法: node update_schedule.js
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 尝试加载 iconv-lite，如果没有则提示安装
let iconv;
try {
    iconv = require('iconv-lite');
} catch (e) {
    console.error('错误: 需要安装 iconv-lite');
    console.error('请运行: npm install iconv-lite');
    process.exit(1);
}

const SINA_CBA_URL = 'https://cba.sports.sina.com.cn/cba/schedule/all/';
const SCRIPT_PATH = path.join(__dirname, 'cba_script.js');

console.log('正在从新浪体育获取CBA赛程数据...\n');

https.get({
    hostname: 'cba.sports.sina.com.cn',
    path: '/cba/schedule/all/',
    headers: { 'User-Agent': 'Mozilla/5.0' }
}, (res) => {
    const chunks = [];
    res.on('data', chunk => chunks.push(chunk));
    res.on('end', () => {
        const buffer = Buffer.concat(chunks);
        const html = iconv.decode(buffer, 'gbk');

        // 提取赛程数据
        const mainTableMatch = html.match(/<div class="part part02[^>]*>(.*?)<\/div>\s*<\/div>\s*<!-- part02 end/s);

        if (!mainTableMatch) {
            console.error('错误: 无法找到赛程表格');
            process.exit(1);
        }

        const tableHtml = mainTableMatch[1];
        const rowMatches = tableHtml.matchAll(/<tr[^>]*class="(odd|even)"[^>]*>(.*?)<\/tr>/gs);

        const schedule = [];
        for (const m of rowMatches) {
            const row = m[2];
            const tdMatches = row.matchAll(/<td[^>]*>(.*?)<\/td>/gs);
            const cells = [];
            for (const td of tdMatches) {
                let text = td[1].replace(/<[^>]+>/g, '').trim()
                    .replace(/&nbsp;/g, ' ')
                    .replace(/&#58;/g, ':');
                cells.push(text);
            }
            if (cells.length >= 5) {
                const [round, datetime, home, score, away] = cells;

                // 判断比赛状态
                let status;
                const today = new Date().toISOString().split('T')[0];
                const gameDate = datetime.split(' ')[0];

                if (score.includes(':') && !score.includes('VS')) {
                    status = '已结束';
                } else if (gameDate === today) {
                    status = '进行中';
                } else {
                    status = '未开始';
                }

                schedule.push({
                    round,
                    datetime,
                    home,
                    score,
                    away,
                    status
                });
            }
        }

        console.log(`获取到 ${schedule.length} 场比赛数据\n`);

        // 显示部分数据
        console.log('=== 今日比赛 ===');
        const today = new Date().toISOString().split('T')[0];
        schedule.filter(s => s.datetime.includes(today)).forEach(g => {
            console.log(`${g.round} | ${g.datetime} | ${g.home} ${g.score} ${g.away} [${g.status}]`);
        });

        // 生成JavaScript代码
        const scheduleCode = schedule.map(game => {
            return `        { round: '${game.round}', datetime: '${game.datetime}', home: '${game.home}', score: '${game.score}', away: '${game.away}', status: '${game.status}' }`;
        }).join(',\n');

        // 读取现有文件
        let scriptContent = fs.readFileSync(SCRIPT_PATH, 'utf8');

        // 更新数据部分
        const dataPattern = /const realSchedule = \[[\s\S]*?\];/;
        const newData = `const realSchedule = [\n${scheduleCode}\n    ];`;

        scriptContent = scriptContent.replace(dataPattern, newData);

        // 更新日期注释
        scriptContent = scriptContent.replace(
            /最后更新: \d{4}-\d{2}-\d{2}/,
            `最后更新: ${today}`
        );

        // 写入文件
        fs.writeFileSync(SCRIPT_PATH, scriptContent, 'utf8');

        console.log('\n数据已更新到 cba_script.js');
        console.log('请提交代码: git add . && git commit -m "Update CBA schedule data" && git push');
    });
}).on('error', e => {
    console.error('请求失败:', e.message);
    process.exit(1);
});